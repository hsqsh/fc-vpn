#!/bin/bash

# 设置变量
REGISTRY="sihan1196"
BACKEND_IMAGE="docker_backend"
GO_API_IMAGE="docker_go-api"
FRONTEND_IMAGE="docker_frontend"
TAG="latest"

# 构建并推送后端镜像
echo "Building and pushing backend image..."
docker build -t ${REGISTRY}/${BACKEND_IMAGE}:${TAG} -f docker/backend.Dockerfile .
docker push ${REGISTRY}/${BACKEND_IMAGE}:${TAG}

# 构建并推送 go-api 镜像
echo "Building and pushing go-api image..."
docker build -t ${REGISTRY}/${GO_API_IMAGE}:${TAG} -f docker/go-api.Dockerfile .
docker push ${REGISTRY}/${GO_API_IMAGE}:${TAG}

# 构建并推送前端镜像
echo "Building and pushing go-api image..."
docker build -t ${REGISTRY}/${FRONTEND_IMAGE}:${TAG} -f docker/frontend.Dockerfile .
docker push ${REGISTRY}/${FRONTEND_IMAGE}:${TAG}

# 拉取最新镜像
echo "Pulling latest images..."
docker pull ${REGISTRY}/${BACKEND_IMAGE}:${TAG}
docker pull ${REGISTRY}/${GO_API_IMAGE}:${TAG}
docker pull ${REGISTRY}/${FRONTEND_IMAGE}:${TAG}

echo "Image update completed successfully!"
