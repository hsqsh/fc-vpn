#!/bin/bash

# ===================================================================
# VPN代理动态缩放部署脚本
# 基于用户数量、连接数量和流量总量的Pod自动缩放
# ===================================================================

set -e

NAMESPACE="vpn-proxy"
SCRIPT_DIR=$(dirname "$(realpath "$0")")

echo "🚀 开始部署VPN代理动态缩放配置..."
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
error_exit() {
    echo -e "${RED}❌ 错误: $1${NC}" >&2
    exit 1
}

# 成功信息函数
success_msg() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 警告信息函数
warning_msg() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 信息函数
info_msg() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查kubectl连接
check_kubectl() {
    info_msg "检查Kubernetes集群连接..."
    if ! kubectl cluster-info &> /dev/null; then
        error_exit "无法连接到Kubernetes集群，请检查kubectl配置"
    fi
    success_msg "Kubernetes集群连接正常"
}

# 检查命名空间
check_namespace() {
    info_msg "检查命名空间 $NAMESPACE..."
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        warning_msg "命名空间 $NAMESPACE 不存在，正在创建..."
        kubectl create namespace $NAMESPACE || error_exit "创建命名空间失败"
    fi
    success_msg "命名空间 $NAMESPACE 已准备就绪"
}

# 检查Prometheus是否安装
check_prometheus() {
    info_msg "检查Prometheus是否已安装..."
    if ! kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus &> /dev/null; then
        warning_msg "未检测到Prometheus，请确保已安装Prometheus Operator"
        echo "可以使用以下命令安装："
        echo "helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
        echo "helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace"
        
        read -p "是否继续部署（某些功能可能无法正常工作）？ [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        success_msg "Prometheus已安装"
    fi
}

# 部署自定义指标API
deploy_custom_metrics_api() {
    info_msg "部署自定义指标API..."
    
    # 生成TLS证书
    if ! kubectl get secret cm-adapter-serving-certs -n $NAMESPACE &> /dev/null; then
        info_msg "生成自签名TLS证书..."
        
        # 创建临时目录
        TEMP_DIR=$(mktemp -d)
        cd $TEMP_DIR
        
        # 生成私钥和证书
        openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
            -keyout tls.key \
            -out tls.crt \
            -subj "/CN=custom-metrics-apiserver.${NAMESPACE}.svc" || error_exit "证书生成失败"
        
        # 创建Secret
        kubectl create secret tls cm-adapter-serving-certs \
            --cert=tls.crt \
            --key=tls.key \
            -n $NAMESPACE || error_exit "创建TLS Secret失败"
        
        # 清理临时文件
        cd - > /dev/null
        rm -rf $TEMP_DIR
        
        success_msg "TLS证书创建完成"
    fi
    
    # 应用自定义指标API配置
    kubectl apply -f "$SCRIPT_DIR/custom-metrics-api.yaml" || error_exit "部署自定义指标API失败"
    success_msg "自定义指标API部署完成"
}

# 部署Prometheus监控配置
deploy_prometheus_monitoring() {
    info_msg "部署Prometheus监控配置..."
    kubectl apply -f "$SCRIPT_DIR/prometheus-monitoring.yaml" || error_exit "部署Prometheus监控配置失败"
    success_msg "Prometheus监控配置部署完成"
}

# 部署HPA配置
deploy_hpa() {
    info_msg "部署Horizontal Pod Autoscaler配置..."
    kubectl apply -f "$SCRIPT_DIR/hpa-backend.yaml" || error_exit "部署HPA配置失败"
    success_msg "HPA配置部署完成"
}

# 等待Pod就绪
wait_for_pods() {
    info_msg "等待Pod启动..."
    
    # 等待自定义指标API Pod就绪
    kubectl wait --for=condition=Ready pod -l app=custom-metrics-apiserver -n $NAMESPACE --timeout=300s || {
        warning_msg "自定义指标API Pod启动超时，请检查日志"
    }
    
    success_msg "所有Pod已启动"
}

# 验证部署
verify_deployment() {
    info_msg "验证部署状态..."
    
    echo -e "\n${BLUE}📊 HPA状态:${NC}"
    kubectl get hpa -n $NAMESPACE
    
    echo -e "\n${BLUE}📈 自定义指标API状态:${NC}"
    kubectl get pods -l app=custom-metrics-apiserver -n $NAMESPACE
    
    echo -e "\n${BLUE}🔍 ServiceMonitor状态:${NC}"
    kubectl get servicemonitor -n $NAMESPACE 2>/dev/null || echo "ServiceMonitor CRD未安装"
    
    echo -e "\n${BLUE}⚙️  当前Pod副本数:${NC}"
    kubectl get deployments -n $NAMESPACE
    
    # 测试自定义指标API
    info_msg "测试自定义指标API..."
    if kubectl top pods -n $NAMESPACE --custom-metrics &> /dev/null; then
        success_msg "自定义指标API工作正常"
    else
        warning_msg "自定义指标API可能需要时间初始化"
    fi
}

# 显示监控信息
show_monitoring_info() {
    echo -e "\n${GREEN}🎉 动态缩放部署完成！${NC}"
    echo "=========================================="
    echo
    echo -e "${BLUE}📋 缩放配置说明:${NC}"
    echo "• Backend Pod: 1-10副本，基于CPU/内存/并发用户/请求数/带宽"
    echo "• Frontend Pod: 2-6副本，基于CPU/内存使用率"
    echo "• 缩放触发阈值:"
    echo "  - 并发用户数 > 50"
    echo "  - 每分钟请求 > 1000"
    echo "  - 带宽使用 > 100Mbps"
    echo "  - CPU使用率 > 70%"
    echo "  - 内存使用率 > 80%"
    echo
    echo -e "${BLUE}🔧 监控命令:${NC}"
    echo "• 查看HPA状态: kubectl get hpa -n $NAMESPACE"
    echo "• 查看Pod状态: kubectl get pods -n $NAMESPACE"
    echo "• 查看缩放事件: kubectl get events -n $NAMESPACE --field-selector reason=SuccessfulRescale"
    echo "• 查看指标: kubectl top pods -n $NAMESPACE"
    echo
    echo -e "${BLUE}📊 访问监控指标:${NC}"
    echo "• Backend指标: http://<backend-service-ip>:5000/metrics"
    echo "• 缩放指标: http://<backend-service-ip>:5000/api/scaling/metrics"
    echo
    echo -e "${YELLOW}⚠️  注意事项:${NC}"
    echo "• 指标收集需要1-2分钟初始化"
    echo "• 缩放动作有稳定窗口，避免频繁波动"
    echo "• 生产环境建议调整阈值和副本数限制"
}

# 主要部署流程
main() {
    echo -e "${GREEN}VPN代理动态缩放部署脚本${NC}"
    echo -e "${GREEN}=====================================`=====${NC}"
    
    check_kubectl
    check_namespace
    check_prometheus
    
    echo
    info_msg "开始部署组件..."
    
    deploy_custom_metrics_api
    deploy_prometheus_monitoring
    deploy_hpa
    
    wait_for_pods
    verify_deployment
    show_monitoring_info
    
    echo -e "\n${GREEN}🚀 所有组件部署完成！${NC}"
}

# 清理函数（可选）
cleanup() {
    echo -e "${YELLOW}🧹 清理动态缩放配置...${NC}"
    
    kubectl delete -f "$SCRIPT_DIR/hpa-backend.yaml" --ignore-not-found=true
    kubectl delete -f "$SCRIPT_DIR/prometheus-monitoring.yaml" --ignore-not-found=true
    kubectl delete -f "$SCRIPT_DIR/custom-metrics-api.yaml" --ignore-not-found=true
    
    success_msg "清理完成"
}

# 命令行参数处理
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "cleanup")
        cleanup
        ;;
    "status")
        verify_deployment
        ;;
    *)
        echo "用法: $0 [deploy|cleanup|status]"
        echo "  deploy  - 部署动态缩放配置（默认）"
        echo "  cleanup - 清理动态缩放配置"
        echo "  status  - 查看部署状态"
        exit 1
        ;;
esac
