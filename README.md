# BabelNet

A cloud-native elastic VPN solution with SOCKS5 proxy functionality, featuring a modern web dashboard and Kubernetes integration simulation.

## Features

- **SOCKS5 Proxy Server**: High-performance traffic forwarding with real-time monitoring
- **Modern Web Dashboard**: Beautiful dark-themed UI with real-time status display
- **User Authentication**: Register/login system with session management
- **Kubernetes Integration**: Mock K8s API for pod/node status monitoring
- **Cloud-Native Ready**: Designed for AWS EKS deployment with auto-scaling

## Project Structure

```
babelnet/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── __init__.py
│   │   ├── proxy.py         # SOCKS5 proxy core logic + API endpoints
│   │   ├── auth.py          # User authentication (register/login)
│   │   ├── k8s_mock.py      # Kubernetes mock API
│   │   └── config.py        # Configuration settings
│   ├── main.py              # FastAPI application entry point
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/                # Vue.js frontend application
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router.js        # Vue Router configuration
│   │   ├── store.js         # Vuex state management
│   │   ├── pages/           # Page components
│   │   │   ├── Dashboard.vue    # Main dashboard
│   │   │   ├── Login.vue        # Login page
│   │   │   ├── Register.vue     # Registration page
│   │   │   ├── Monitor.vue      # Traffic monitoring
│   │   │   └── Profile.vue      # User profile
│   │   └── components/      # Reusable components
│   │       ├── NetworkStatus.vue
│   │       └── TrafficMonitor.vue
│   ├── public/
│   │   └── index.html
│   ├── package.json
│   ├── vue.config.js        # Vue CLI configuration with proxy
│   └── README.md           # Frontend documentation
├── docker/                  # Docker deployment files
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
├── docs/                    # Project documentation
│   ├── proposal.md
│   └── proposal.pdf
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd babelnet
   ```

2. **Start Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
   Backend will be available at: http://localhost:8000

3. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run serve
   ```
   Frontend will be available at: http://localhost:8080
   
   默认端口是 8080，但如被占用可能会自动变为 8081、8082 等。建议启动后看终端输出，确认实际端口。

4. **Access the Application**
   - Dashboard: http://localhost:8080/#/
   - Login: http://localhost:8080/#/login
   - Register: http://localhost:8080/#/register

### Docker/Podman Deployment

#### 使用通用部署脚本（推荐）
```bash
# 启动所有服务
./scripts/deploy.sh up

# 构建镜像
./scripts/deploy.sh build

# 停止服务
./scripts/deploy.sh down

# 查看日志
./scripts/deploy.sh logs

# 查看帮助
./scripts/deploy.sh help
```

#### 手动部署

**Docker 用户:**
```bash
cd docker
docker-compose up --build
```

**Podman 用户:**
```bash
# 安装 podman-compose
pip install podman-compose

# 启动服务
cd docker
podman-compose -f podman-compose.yml up --build
```

## ✨Docker 镜像部署（给组员）

⚠️如果你不想本地构建镜像，可以直接拉取我推送到 Docker Hub 的镜像。

### 步骤

1. **拉取镜像**

```bash
# 拉取后端镜像
docker pull oliviaaa77/docker_backend:latest

# 拉取前端镜像
docker pull oliviaaa77/docker_frontend:latest
```

2. **编辑 docker-compose.yml**

在 `docker/docker-compose.yml` 中，将 `build:` 字段注释掉或删除，改为 `image:` 字段。例如：

```yaml
services:
  backend:
    # build:
    #   context: ..
    #   dockerfile: docker/backend.Dockerfile
    image: oliviaaa77/docker_backend:latest
    container_name: babelnet-backend
    ports:
      - "8000:8000"
      - "8888:8888"
    environment:
      - LISTEN_HOST=0.0.0.0
      - LISTEN_PORT=8888
    networks:
      - babelnet-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    # build:
    #   context: ..
    #   dockerfile: docker/frontend.Dockerfile
    image: oliviaaa77/docker_frontend:latest
    container_name: babelnet-frontend
    ports:
      - "8080:80"
    depends_on:
      - backend
    networks:
      - babelnet-network
    restart: unless-stopped

networks:
  babelnet-network:
    driver: bridge
```

3. **启动服务**

```bash
cd docker
docker-compose up -d
```

4. **访问服务**
- 前端：http://localhost:8080
- 后端API：http://localhost:8000

---

**注意：**
- 组员只需要安装 Docker 和 docker-compose，不需要 Podman。
- 如果端口被占用，可以自行修改 `docker-compose.yml` 里的端口映射。
- 如需更新镜像，先 `docker pull` 再 `docker-compose up -d`。

## API Documentation

### Authentication Endpoints

- `