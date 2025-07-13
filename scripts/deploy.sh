#!/bin/bash

# BabelNet 通用部署脚本
# 自动检测 Docker 或 Podman 并选择合适的命令

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检测容器运行时
detect_runtime() {
    if command -v docker &> /dev/null && docker --version &> /dev/null; then
        echo "docker"
    elif command -v podman &> /dev/null && podman --version &> /dev/null; then
        echo "podman"
    else
        echo "none"
    fi
}

# 检测 compose 工具
detect_compose() {
    local runtime=$1
    
    if [ "$runtime" = "docker" ]; then
        if command -v docker-compose &> /dev/null; then
            echo "docker-compose"
        elif docker compose version &> /dev/null 2>&1; then
            echo "docker compose"
        else
            echo "none"
        fi
    elif [ "$runtime" = "podman" ]; then
        if command -v podman-compose &> /dev/null; then
            echo "podman-compose"
        else
            echo "none"
        fi
    else
        echo "none"
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}BabelNet 部署脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build    构建镜像"
    echo "  up       启动服务"
    echo "  down     停止服务"
    echo "  restart  重启服务"
    echo "  logs     查看日志"
    echo "  clean    清理容器和镜像"
    echo "  help     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 up        # 启动所有服务"
    echo "  $0 build     # 构建镜像"
    echo "  $0 down      # 停止服务"
}

# 构建镜像
build_images() {
    local runtime=$1
    local compose_tool=$2
    
    echo -e "${YELLOW}构建镜像...${NC}"
    
    if [ "$runtime" = "docker" ]; then
        if [ "$compose_tool" = "docker-compose" ]; then
            docker-compose -f docker/docker-compose.yml build
        else
            docker compose -f docker/docker-compose.yml build
        fi
    elif [ "$runtime" = "podman" ]; then
        if [ "$compose_tool" = "podman-compose" ]; then
            podman-compose -f docker/podman-compose.yml build
        else
            echo -e "${RED}错误: 未找到 podman-compose${NC}"
            echo "请安装 podman-compose: pip install podman-compose"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}镜像构建完成!${NC}"
}

# 启动服务
start_services() {
    local runtime=$1
    local compose_tool=$2
    
    echo -e "${YELLOW}启动服务...${NC}"
    
    if [ "$runtime" = "docker" ]; then
        if [ "$compose_tool" = "docker-compose" ]; then
            docker-compose -f docker/docker-compose.yml up -d
        else
            docker compose -f docker/docker-compose.yml up -d
        fi
    elif [ "$runtime" = "podman" ]; then
        if [ "$compose_tool" = "podman-compose" ]; then
            podman-compose -f docker/podman-compose.yml up -d
        else
            echo -e "${RED}错误: 未找到 podman-compose${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}服务启动完成!${NC}"
    echo -e "${BLUE}前端访问地址: http://localhost${NC}"
    echo -e "${BLUE}后端API地址: http://localhost:8000${NC}"
    echo -e "${BLUE}API文档: http://localhost:8000/docs${NC}"
}

# 停止服务
stop_services() {
    local runtime=$1
    local compose_tool=$2
    
    echo -e "${YELLOW}停止服务...${NC}"
    
    if [ "$runtime" = "docker" ]; then
        if [ "$compose_tool" = "docker-compose" ]; then
            docker-compose -f docker/docker-compose.yml down
        else
            docker compose -f docker/docker-compose.yml down
        fi
    elif [ "$runtime" = "podman" ]; then
        if [ "$compose_tool" = "podman-compose" ]; then
            podman-compose -f docker/podman-compose.yml down
        else
            echo -e "${RED}错误: 未找到 podman-compose${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}服务已停止!${NC}"
}

# 重启服务
restart_services() {
    local runtime=$1
    local compose_tool=$2
    
    echo -e "${YELLOW}重启服务...${NC}"
    stop_services "$runtime" "$compose_tool"
    start_services "$runtime" "$compose_tool"
}

# 查看日志
show_logs() {
    local runtime=$1
    local compose_tool=$2
    
    echo -e "${YELLOW}查看服务日志...${NC}"
    
    if [ "$runtime" = "docker" ]; then
        if [ "$compose_tool" = "docker-compose" ]; then
            docker-compose -f docker/docker-compose.yml logs -f
        else
            docker compose -f docker/docker-compose.yml logs -f
        fi
    elif [ "$runtime" = "podman" ]; then
        if [ "$compose_tool" = "podman-compose" ]; then
            podman-compose -f docker/podman-compose.yml logs -f
        else
            echo -e "${RED}错误: 未找到 podman-compose${NC}"
            exit 1
        fi
    fi
}

# 清理资源
clean_resources() {
    local runtime=$1
    
    echo -e "${YELLOW}清理容器和镜像...${NC}"
    
    if [ "$runtime" = "docker" ]; then
        docker system prune -f
        docker image prune -f
    elif [ "$runtime" = "podman" ]; then
        podman system prune -f
        podman image prune -f
    fi
    
    echo -e "${GREEN}清理完成!${NC}"
}

# 主函数
main() {
    local action=${1:-help}
    
    # 检测容器运行时
    local runtime=$(detect_runtime)
    if [ "$runtime" = "none" ]; then
        echo -e "${RED}错误: 未找到 Docker 或 Podman${NC}"
        echo "请安装 Docker 或 Podman:"
        echo "  Docker: https://docs.docker.com/get-docker/"
        echo "  Podman: https://podman.io/getting-started/installation"
        exit 1
    fi
    
    # 检测 compose 工具
    local compose_tool=$(detect_compose "$runtime")
    if [ "$compose_tool" = "none" ]; then
        echo -e "${RED}错误: 未找到 compose 工具${NC}"
        if [ "$runtime" = "podman" ]; then
            echo "请安装 podman-compose: pip install podman-compose"
        else
            echo "请安装 docker-compose 或使用 Docker Desktop"
        fi
        exit 1
    fi
    
    echo -e "${BLUE}检测到运行时: $runtime${NC}"
    echo -e "${BLUE}使用 compose 工具: $compose_tool${NC}"
    echo ""
    
    # 执行操作
    case $action in
        build)
            build_images "$runtime" "$compose_tool"
            ;;
        up)
            start_services "$runtime" "$compose_tool"
            ;;
        down)
            stop_services "$runtime" "$compose_tool"
            ;;
        restart)
            restart_services "$runtime" "$compose_tool"
            ;;
        logs)
            show_logs "$runtime" "$compose_tool"
            ;;
        clean)
            clean_resources "$runtime"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@" 