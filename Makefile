# BabelNet Makefile
# 支持 Docker 和 Podman 的跨平台构建和部署

.PHONY: help build up down restart logs clean install-podman install-docker

# 默认目标
help:
	@echo "BabelNet 构建和部署工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make build      - 构建 Docker/Podman 镜像"
	@echo "  make up         - 启动所有服务"
	@echo "  make down       - 停止所有服务"
	@echo "  make restart    - 重启所有服务"
	@echo "  make logs       - 查看服务日志"
	@echo "  make clean      - 清理容器和镜像"
	@echo "  make dev        - 本地开发模式"
	@echo "  make install-podman  - 安装 Podman (macOS)"
	@echo "  make install-docker   - 安装 Docker (macOS)"
	@echo ""

# 检测容器运行时
DETECT_RUNTIME := $(shell if command -v docker >/dev/null 2>&1 && docker --version >/dev/null 2>&1; then echo "docker"; elif command -v podman >/dev/null 2>&1 && podman --version >/dev/null 2>&1; then echo "podman"; else echo "none"; fi)

# 检测 compose 工具
ifeq ($(DETECT_RUNTIME),docker)
    DETECT_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; elif docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "none"; fi)
else ifeq ($(DETECT_RUNTIME),podman)
    DETECT_COMPOSE := $(shell if command -v podman-compose >/dev/null 2>&1; then echo "podman-compose"; else echo "none"; fi)
else
    DETECT_COMPOSE := none
endif

# 检查运行时
check-runtime:
	@if [ "$(DETECT_RUNTIME)" = "none" ]; then \
		echo "错误: 未找到 Docker 或 Podman"; \
		echo "请运行 'make install-docker' 或 'make install-podman'"; \
		exit 1; \
	fi
	@if [ "$(DETECT_COMPOSE)" = "none" ]; then \
		echo "错误: 未找到 compose 工具"; \
		if [ "$(DETECT_RUNTIME)" = "podman" ]; then \
			echo "请安装 podman-compose: pip install podman-compose"; \
		else \
			echo "请安装 docker-compose 或使用 Docker Desktop"; \
		fi; \
		exit 1; \
	fi
	@echo "检测到运行时: $(DETECT_RUNTIME)"
	@echo "使用 compose 工具: $(DETECT_COMPOSE)"

# 构建镜像
build: check-runtime
	@echo "构建镜像..."
ifeq ($(DETECT_RUNTIME),docker)
ifeq ($(DETECT_COMPOSE),docker-compose)
	docker-compose -f docker/docker-compose.yml build
else
	docker compose -f docker/docker-compose.yml build
endif
else ifeq ($(DETECT_RUNTIME),podman)
	podman-compose -f docker/podman-compose.yml build
endif
	@echo "镜像构建完成!"

# 启动服务
up: check-runtime
	@echo "启动服务..."
ifeq ($(DETECT_RUNTIME),docker)
ifeq ($(DETECT_COMPOSE),docker-compose)
	docker-compose -f docker/docker-compose.yml up -d
else
	docker compose -f docker/docker-compose.yml up -d
endif
else ifeq ($(DETECT_RUNTIME),podman)
	podman-compose -f docker/podman-compose.yml up -d
endif
	@echo "服务启动完成!"
	@echo "前端访问地址: http://localhost"
	@echo "后端API地址: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"

# 停止服务
down: check-runtime
	@echo "停止服务..."
ifeq ($(DETECT_RUNTIME),docker)
ifeq ($(DETECT_COMPOSE),docker-compose)
	docker-compose -f docker/docker-compose.yml down
else
	docker compose -f docker/docker-compose.yml down
endif
else ifeq ($(DETECT_RUNTIME),podman)
	podman-compose -f docker/podman-compose.yml down
endif
	@echo "服务已停止!"

# 重启服务
restart: down up

# 查看日志
logs: check-runtime
	@echo "查看服务日志..."
ifeq ($(DETECT_RUNTIME),docker)
ifeq ($(DETECT_COMPOSE),docker-compose)
	docker-compose -f docker/docker-compose.yml logs -f
else
	docker compose -f docker/docker-compose.yml logs -f
endif
else ifeq ($(DETECT_RUNTIME),podman)
	podman-compose -f docker/podman-compose.yml logs -f
endif

# 清理资源
clean: check-runtime
	@echo "清理容器和镜像..."
ifeq ($(DETECT_RUNTIME),docker)
	docker system prune -f
	docker image prune -f
else ifeq ($(DETECT_RUNTIME),podman)
	podman system prune -f
	podman image prune -f
endif
	@echo "清理完成!"

# 本地开发模式
dev:
	@echo "启动本地开发模式..."
	@echo "请分别启动后端和前端服务:"
	@echo ""
	@echo "后端:"
	@echo "  cd backend && pip install -r requirements.txt && uvicorn main:app --reload"
	@echo ""
	@echo "前端:"
	@echo "  cd frontend && npm install && npm run serve"
	@echo ""
	@echo "访问地址:"
	@echo "  前端: http://localhost:8080"
	@echo "  后端: http://localhost:8000"

# 安装 Podman (macOS)
install-podman:
	@echo "安装 Podman..."
ifeq ($(OS),Darwin)
	@if command -v brew >/dev/null 2>&1; then \
		brew install podman; \
		podman machine init; \
		podman machine start; \
		echo "Podman 安装完成!"; \
		echo "请运行: pip install podman-compose"; \
	else \
		echo "错误: 未找到 Homebrew"; \
		echo "请先安装 Homebrew: https://brew.sh"; \
		exit 1; \
	fi
else
	@echo "错误: 此命令仅支持 macOS"
	@echo "请参考 docs/podman-setup.md 了解其他系统的安装方法"
endif

# 安装 Docker (macOS)
install-docker:
	@echo "安装 Docker..."
ifeq ($(OS),Darwin)
	@if command -v brew >/dev/null 2>&1; then \
		brew install --cask docker; \
		echo "Docker 安装完成!"; \
		echo "请启动 Docker Desktop 应用程序"; \
	else \
		echo "错误: 未找到 Homebrew"; \
		echo "请先安装 Homebrew: https://brew.sh"; \
		exit 1; \
	fi
else
	@echo "错误: 此命令仅支持 macOS"
	@echo "请访问 https://docs.docker.com/get-docker/ 了解其他系统的安装方法"
endif

# 检查系统信息
info:
	@echo "系统信息:"
	@echo "  操作系统: $(shell uname -s)"
	@echo "  架构: $(shell uname -m)"
	@echo "  容器运行时: $(DETECT_RUNTIME)"
	@echo "  Compose 工具: $(DETECT_COMPOSE)"
	@echo ""
	@if [ "$(DETECT_RUNTIME)" != "none" ]; then \
		if [ "$(DETECT_RUNTIME)" = "docker" ]; then \
			docker --version; \
		else \
			podman --version; \
		fi; \
	fi 