# 🚀 VPN代理服务 EKS 零基础部署指南

## 📋 部署概述

本指南将帮助您在全新的EKS集群上从零开始部署VPN代理服务，包括：
- ✅ 后端Flask API服务 (Python)
- ✅ 前端Web界面 (Vue.js + Nginx)
- ✅ Redis缓存服务
- ✅ 自动缩放配置 (HPA)
- ✅ 负载均衡器 (AWS LoadBalancer)

## 🏗️ 架构图

```
Internet
    ↓
AWS LoadBalancer (NLB)
    ↓
Frontend Pods (2-8个)
    ↓ (Nginx反向代理)
Backend Pods (1-10个) ← → Redis Pod
    ↓
VPN代理服务 (8888端口)
```

## 📁 部署文件说明

| 文件名 | 功能描述 | 部署顺序 |
|--------|----------|----------|
| `namespace.yaml` | 创建vpn-proxy命名空间 | 1 |
| `redis-deployment.yaml` | Redis缓存服务 | 2 |
| `nginx-configmap.yaml` | Nginx反向代理配置 | 3 |
| `backend-deployment.yaml` | 后端API服务 | 4 |
| `frontend-deployment.yaml` | 前端Web服务 | 5 |
| `hpa-autoscaling.yaml` | 自动缩放配置 | 6 |

## 🛠️ 快速部署

### 方法1: 一键部署脚本 (推荐)

```powershell
# 进入k8s目录
cd "C:\Users\20399\Desktop\VPN-final\VPN\k8s"

# 执行一键部署
.\deploy-full.ps1

# 如果需要先验证配置
.\deploy-full.ps1 -DryRun
```

### 方法2: 手动分步部署

```powershell
# 1. 创建命名空间
kubectl apply -f namespace.yaml

# 2. 部署Redis
kubectl apply -f redis-deployment.yaml

# 3. 部署Nginx配置
kubectl apply -f nginx-configmap.yaml

# 4. 部署后端服务
kubectl apply -f backend-deployment.yaml

# 5. 部署前端服务
kubectl apply -f frontend-deployment.yaml

# 6. 部署自动缩放
kubectl apply -f hpa-autoscaling.yaml
```

## 📊 监控和验证

### 检查部署状态
```powershell
# 查看所有Pod状态
kubectl get pods -n vpn-proxy -o wide

# 查看服务状态
kubectl get services -n vpn-proxy

# 查看HPA状态
kubectl get hpa -n vpn-proxy

# 查看事件
kubectl get events -n vpn-proxy --sort-by='.lastTimestamp'
```

### 获取访问地址
```powershell
# 前端访问地址
kubectl get service frontend-service -n vpn-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# 后端API地址
kubectl get service backend-service -n vpn-proxy -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## 🔧 资源配置详情

### 后端服务配置
- **CPU请求**: 200m, **限制**: 500m
- **内存请求**: 256Mi, **限制**: 512Mi
- **端口**: 5000 (API), 8888 (代理)
- **副本数**: 1-10个 (自动缩放)

### 前端服务配置
- **CPU请求**: 100m, **限制**: 200m
- **内存请求**: 128Mi, **限制**: 256Mi
- **端口**: 80 (HTTP)
- **副本数**: 2-8个 (自动缩放)

### Redis配置
- **CPU请求**: 100m, **限制**: 200m
- **内存请求**: 64Mi, **限制**: 128Mi
- **副本数**: 1个 (固定)

## 📈 自动缩放触发条件

### 后端服务 (backend-hpa)
- **扩容触发**: CPU > 70% 或 内存 > 80%
- **缩容触发**: CPU < 70% 且 内存 < 80% (持续5分钟)
- **扩容策略**: 最多翻倍，每60秒最多+2个Pod
- **缩容策略**: 最多减半，每60秒最多-1个Pod

### 前端服务 (frontend-hpa)
- **扩容触发**: CPU > 60% 或 内存 > 70%
- **缩容触发**: CPU < 60% 且 内存 < 70% (持续5分钟)
- **扩容策略**: 最多+50%，每120秒最多+2个Pod
- **缩容策略**: 最多-25%，每120秒最多-1个Pod

## 🌐 服务访问

部署成功后，您将获得以下访问地址：

1. **前端Web界面**: `http://<frontend-lb-hostname>`
2. **后端API**: `http://<backend-lb-hostname>:5000`
3. **代理服务**: `<backend-lb-hostname>:8888`

## 🔍 故障排查

### 常见问题

#### 1. Pod无法启动
```powershell
# 查看Pod详细信息
kubectl describe pod <pod-name> -n vpn-proxy

# 查看Pod日志
kubectl logs <pod-name> -n vpn-proxy
```

#### 2. 镜像拉取失败
```powershell
# 检查ECR认证
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 782486516265.dkr.ecr.us-east-1.amazonaws.com

# 检查镜像是否存在
aws ecr describe-images --repository-name vpn-backend --region us-east-1
aws ecr describe-images --repository-name vpn-frontend --region us-east-1
```

#### 3. LoadBalancer未分配外部IP
```powershell
# 检查LoadBalancer状态
kubectl describe service frontend-service -n vpn-proxy
kubectl describe service backend-service -n vpn-proxy

# 通常需要等待2-3分钟
kubectl get services -n vpn-proxy -w
```

#### 4. HPA无法获取指标
```powershell
# 检查metrics-server
kubectl get deployment metrics-server -n kube-system

# 安装metrics-server (如果未安装)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 为EKS配置metrics-server
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

## 🧹 清理部署

如果需要删除所有部署的资源：

```powershell
# 删除所有资源
kubectl delete namespace vpn-proxy

# 或者逐个删除
kubectl delete -f hpa-autoscaling.yaml
kubectl delete -f frontend-deployment.yaml
kubectl delete -f backend-deployment.yaml
kubectl delete -f nginx-configmap.yaml
kubectl delete -f redis-deployment.yaml
kubectl delete -f namespace.yaml
```

## 📞 支持信息

- **部署脚本**: `deploy-full.ps1`
- **配置文件目录**: `k8s/`
- **镜像仓库**: ECR (782486516265.dkr.ecr.us-east-1.amazonaws.com)
- **命名空间**: `vpn-proxy`

---

**注意**: 确保您的EKS集群有足够的资源来运行所有服务，建议至少2个t3.medium或更高配置的工作节点。
