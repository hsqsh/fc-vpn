# 构建阶段
FROM node:16-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY frontend/package*.json ./

# 安装依赖
RUN npm install --omit=dev

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine as production-stage

# 复制构建产物到 nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"] 