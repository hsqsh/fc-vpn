# 多阶段构建 - 构建阶段
FROM golang:1.20-alpine AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache git ca-certificates tzdata

# 设置 Go 环境变量
ENV GOPROXY=https://proxy.golang.org,direct \
    GOSUMDB=sum.golang.org \
    GO111MODULE=on \
    CGO_ENABLED=0

# 复制 go.mod 和 go.sum（如果存在）
COPY go-api/go.mod go-api/go.sum* ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY go-api/ .

# 构建应用 - 支持多架构
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o script .

# 运行阶段
FROM alpine:latest

# 安装运行时依赖
RUN apk --no-cache add ca-certificates tzdata curl

# 设置工作目录
WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/script .

# 设置权限
RUN chmod +x ./script

# 暴露端口（根据你的go-api实际端口调整）
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# 启动命令
CMD ["./script"]