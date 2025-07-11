# 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# 构建后端
FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# 生产环境镜像
FROM python:3.11-slim
WORKDIR /app

# 复制后端代码
COPY --from=backend-builder /app/backend ./backend

# 复制前端构建产物到后端 static 目录
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# 暴露端口
EXPOSE 5000

# 启动命令
WORKDIR /app/backend
CMD ["flask", "run"]
