# 代理服务管理平台

基于 Vue3 + Flask 架构的现代化代理服务管理平台，支持本地部署和 Kubernetes 集群部署。

## 功能特性

- 🚀 现代化 Web 界面管理
- 📊 实时流量监控和统计
- 🔧 SOCKS5 代理服务
- 📈 可视化数据图表
- 🐳 Docker 容器化部署
- ☸️ Kubernetes 集群支持
- 🔄 自动扩缩容
- 💾 持久化配置存储

## 技术栈

### 前端
- Vue 3
- Element Plus
- ECharts
- Socket.IO Client
- Vite

### 后端
- Flask
- Socket.IO
- Python Socket
- Gunicorn

### 部署
- Docker & Docker Compose
- Kubernetes
- AWS EKS

## 快速开始

### 本地开发

1. **安装后端依赖**
```bash
pip install -r requirements.txt
```

2. **安装前端依赖**
```bash
cd frontend
npm install
```

3. **启动后端服务**
```bash
python app.py
```

4. **启动前端开发服务器**
```bash
cd frontend
npm run dev
```

5. **访问应用**
- Web 界面: http://localhost:3000
- API 端点: http://localhost:5000
- SOCKS5 代理: localhost:8888

### Docker 部署

1. **构建镜像**
```bash
docker build -t proxy-web:latest .
```

2. **使用 Docker Compose 启动**
```bash
docker-compose up -d
```

3. **访问应用**
- Web 界面: http://localhost:5000
- SOCKS5 代理: localhost:8888

### Kubernetes 部署

1. **部署到 K8s 集群**
```bash
kubectl apply -f k8s/deployment.yaml
```

2. **查看服务状态**
```bash
kubectl get pods -n proxy-service
kubectl get svc -n proxy-service
```

## API 文档

### 代理控制
- `GET /api/proxy/status` - 获取代理状态
- `POST /api/proxy/start` - 启动代理服务
- `POST /api/proxy/stop` - 停止代理服务
- `POST /api/proxy/test` - 测试代理连接

### 健康检查
- `GET /health` - 健康状态检查
- `GET /ready` - 就绪状态检查

## 配置说明

### 环境变量
- `FLASK_ENV`: Flask 运行环境 (development/production)
- `FLASK_APP`: Flask 应用入口文件

### 代理配置
- 默认端口: 8888
- 支持协议: SOCKS5
- 认证方式: 无认证

## 监控和日志

- 实时连接监控
- 流量统计图表
- WebSocket 实时数据推送
- 结构化日志输出

## 安全考虑

- 非 root 用户运行
- 容器安全配置
- 资源限制
- 健康检查

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
