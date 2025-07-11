# fc-vpn

一个简单的流量转发代理系统，包含前后端，模拟接入 Kubernetes 场景。

## 目录结构
- backend/   # FastAPI 后端
- frontend/  # Vue 前端
- docker/    # Docker 部署相关
- docs/      # 文档资料

## 快速开始

### 本地开发
后端：
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
前端：
```bash
cd frontend
npm install
npm run serve
```

### Docker 一键启动
```bash
cd docker
# TODO: 按需完善 Dockerfile 后
# docker-compose up --build
```

## 功能说明
- 流量转发代理
- K8s 场景模拟
- 前后端分离

## 文档
详见 docs/