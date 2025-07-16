#!/bin/bash

# 构建并推送多架构 backend 镜像到 Docker Hub
# 用法：bash scripts/build-and-push-backend.sh

set -e

IMAGE=oliviaaa77/babelnet-backend
CONTEXT=.
DOCKERFILE=docker/backend.Dockerfile

# 1. 构建 amd64 镜像
podman build --arch amd64 -f $DOCKERFILE -t ${IMAGE}:amd64 $CONTEXT

# 2. 构建 arm64 镜像
podman build --arch arm64 -f $DOCKERFILE -t ${IMAGE}:arm64 $CONTEXT

# 3. 推送两个架构的镜像
podman push ${IMAGE}:amd64
podman push ${IMAGE}:arm64

# 4. manifest 创建前，先清理同名 manifest/镜像，防止冲突
podman rmi ${IMAGE}:latest || true

# 5. 创建并推送 manifest
podman manifest create ${IMAGE}:latest
podman manifest add ${IMAGE}:latest docker://${IMAGE}:amd64
podman manifest add ${IMAGE}:latest docker://${IMAGE}:arm64
podman manifest push --all ${IMAGE}:latest docker://${IMAGE}:latest

# 6. 脚本末尾，清理所有相关镜像
podman rmi ${IMAGE}:amd64 || true
podman rmi ${IMAGE}:arm64 || true
podman rmi ${IMAGE}:latest || true

echo "Multi-arch backend image build, push, and cleanup complete!" 