# fc-vpn

一个简单的流量转发代理系统，包含前后端，模拟接入 Kubernetes 场景。

## 目录结构
- backend/   # FastAPI 后端
- frontend/  # Vue 前端
- docker/    # Docker 部署相关
- docs/      # 文档资料

```
fc-vpn/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── proxy.py         # 代理/转发核心逻辑
│   │   ├── k8s_mock.py      # K8s 场景模拟接口
│   │   └── config.py        # 配置
│   ├── main.py              # FastAPI 启动入口
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router.js
│   │   ├── store.js
│   │   ├── pages/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Login.vue
│   │   │   ├── Monitor.vue
│   │   │   └── Profile.vue
│   │   └── components/
│   │       ├── NetworkStatus.vue
│   │       └── TrafficMonitor.vue
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── README.md
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
│
├── README.md
└── docs/
    ├── proposal.md
    └── proposal.pdf
```


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