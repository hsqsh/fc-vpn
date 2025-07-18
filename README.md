# ☁️ VPN代理服务 - 云端部署完整指南

## 📋 项目概述

这是一个完整的VPN代理服务系统，包含：
- **后端服务**: Flask API + WebSocket + HTTP代理服务器
- **前端界面**: Vue.js + Element Plus 现代化Web管理界面
- **缓存服务**: Redis 会话存储和数据缓存
- **容器化**: Docker镜像 + Kubernetes自动化部署
- **云原生**: AWS EKS + ECR + 自动伸缩

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────┬───────────────────────────────────────┘
                     │
┌─────────────────────▼───────────────────────────────────────┐
│              AWS Application Load Balancer                  │
│              (支持HTTP/HTTPS + SSL终止)                      │
└─────────────────────┬───────────────────────────────────────┘
                     │
┌─────────────────────▼───────────────────────────────────────┐
│                 EKS Cluster                                 │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Frontend Pods  │    │  Backend Pods   │                │
│  │  (Vue.js)       │◄──►│  (Flask API)    │                │
│  │  Port: 80       │    │  Port: 5000     │                │
│  │  Replicas: 2-8  │    │  Port: 8888     │                │
│  └─────────────────┘    │  Replicas: 1-10 │                │
│           │              └─────────┬───────┘                │
│           │                       │                        │
│  ┌─────────▼───────────────────────▼───────┐                │
│  │           Redis Cache                   │                │
│  │        (会话存储 + 数据缓存)              │                │
│  │           Port: 6379                    │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

### 后端 (Backend)
- **Python 3.11+**
- **Flask 2.3.3** - REST API框架
- **Flask-SocketIO 5.3.6** - WebSocket实时通信
- **Gunicorn 21.2.0** - WSGI生产服务器
- **Redis** - 缓存和会话存储

### 前端 (Frontend)
- **Vue.js 3.3.4** - 现代化前端框架
- **Element Plus 2.3.14** - UI组件库
- **Vite 4.5.14** - 构建工具
- **Nginx** - 静态文件服务器

### 云基础设施
- **AWS EKS** - Kubernetes管理服务
- **AWS ECR** - 容器镜像仓库
- **AWS Application Load Balancer** - 负载均衡
- **Kubernetes HPA** - 水平自动伸缩

## 📋 部署前准备

### 1. 安装必要工具

```powershell
# 安装 AWS CLI
winget install Amazon.AWSCLI

# 安装 kubectl
winget install Kubernetes.kubectl

# 安装 Docker Desktop
winget install Docker.DockerDesktop

# 验证安装
aws --version
kubectl version --client
docker --version
```

### 2. AWS账户配置

```powershell
# 配置AWS凭证
aws configure
# AWS Access Key ID: [输入您的Access Key]
# AWS Secret Access Key: [输入您的Secret Key]
# Default region name: us-east-1
# Default output format: json

# 验证配置
aws sts get-caller-identity
```

### 3. 创建ECR仓库

```powershell
# 创建后端镜像仓库
aws ecr create-repository --repository-name vpn-backend --region us-east-1

# 创建前端镜像仓库
aws ecr create-repository --repository-name vpn-frontend --region us-east-1

# 获取ECR登录token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 782486516265.dkr.ecr.us-east-1.amazonaws.com
```

### 4. 创建EKS集群

```powershell
# 安装eksctl
winget install weaveworks.eksctl

# 创建EKS集群 (大约需要15-20分钟)
eksctl create cluster \
    --name vpn-proxy-cluster \
    --region us-east-1 \
    --version 1.27 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 2 \
    --nodes-min 1 \
    --nodes-max 4 \
    --managed

# 配置kubectl上下文
aws eks update-kubeconfig --region us-east-1 --name vpn-proxy-cluster

# 验证集群连接
kubectl get nodes
```

## 🐳 镜像构建和推送

### 步骤1: 构建后端镜像

```powershell
# 切换到项目根目录
cd "C:\Users\20399\Desktop\VPN-final\VPN"

# 构建后端镜像
docker build -f Dockerfile.backend -t vpn-backend:latest .

# 标记镜像
docker tag vpn-backend:latest 782486516265.dkr.ecr.us-east-1.amazonaws.com/vpn-backend:latest

# 推送到ECR
docker push 782486516265.dkr.ecr.us-east-1.amazonaws.com/vpn-backend:latest
```

### 步骤2: 构建前端镜像

```powershell
# 构建前端镜像
docker build -f Dockerfile.frontend -t vpn-frontend:latest .

# 标记镜像
docker tag vpn-frontend:latest 782486516265.dkr.ecr.us-east-1.amazonaws.com/vpn-frontend:latest

# 推送到ECR
docker push 782486516265.dkr.ecr.us-east-1.amazonaws.com/vpn-frontend:latest
```

### 步骤3: 验证镜像推送

```powershell
# 列出ECR中的镜像
aws ecr list-images --repository-name vpn-backend --region us-east-1
aws ecr list-images --repository-name vpn-frontend --region us-east-1
```

## 🚀 Kubernetes部署



```powershell
# 1. 创建命名空间
kubectl apply -f namespace.yaml

# 2. 部署Redis缓存服务
kubectl apply -f redis-deployment.yaml

# 3. 创建Nginx配置
kubectl apply -f nginx-configmap.yaml

# 4. 部署后端服务
kubectl apply -f backend-deployment.yaml

# 5. 部署前端服务
kubectl apply -f frontend-deployment.yaml

# 6. 配置自动伸缩
kubectl apply -f hpa-autoscaling.yaml
```

### 验证部署状态

```powershell
# 检查所有资源
kubectl get all -n vpn-proxy

# 检查Pod状态
kubectl get pods -n vpn-proxy

# 检查服务状态
kubectl get services -n vpn-proxy

# 检查HPA状态
kubectl get hpa -n vpn-proxy

# 查看Pod日志
kubectl logs -f deployment/backend-deployment -n vpn-proxy
kubectl logs -f deployment/frontend-deployment -n vpn-proxy
```

## 🌐 访问应用

### 获取外部访问地址

```powershell
# 获取LoadBalancer外部IP
kubectl get service frontend-service -n vpn-proxy

# 等待EXTERNAL-IP分配完成 (可能需要2-5分钟)
kubectl get service frontend-service -n vpn-proxy -w
```

### 访问应用

```powershell
# 获取前端访问地址
$FRONTEND_URL = kubectl get service frontend-service -n vpn-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
Write-Host "前端地址: http://$FRONTEND_URL"

# 获取后端API地址
$BACKEND_URL = kubectl get service backend-service -n vpn-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
Write-Host "后端API: http://$BACKEND_URL:5000"
Write-Host "代理服务: http://$BACKEND_URL:8888"
```

## 📊 监控和维护

### 查看实时状态

```powershell
# 监控Pod状态
kubectl get pods -n vpn-proxy -w

# 监控HPA自动伸缩
kubectl get hpa -n vpn-proxy -w

# 查看集群资源使用
kubectl top nodes
kubectl top pods -n vpn-proxy
```

### 扩缩容操作

```powershell
# 手动扩容后端
kubectl scale deployment backend-deployment --replicas=3 -n vpn-proxy

# 手动扩容前端
kubectl scale deployment frontend-deployment --replicas=4 -n vpn-proxy

# 查看扩容状态
kubectl rollout status deployment/backend-deployment -n vpn-proxy
```

### 日志查看

```powershell
# 查看后端日志
kubectl logs -f deployment/backend-deployment -n vpn-proxy

# 查看前端日志
kubectl logs -f deployment/frontend-deployment -n vpn-proxy

# 查看Redis日志
kubectl logs -f deployment/redis-deployment -n vpn-proxy
```

