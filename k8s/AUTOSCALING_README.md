# VPN代理动态Pod缩放配置指南

## 📋 概述

本配置实现了基于多指标的Kubernetes Pod自动缩放，能够根据用户数量、连接数量、流量总量和系统资源使用情况动态调整Pod副本数。

## 🏗️ 架构组件

### 1. 核心组件
- **Horizontal Pod Autoscaler (HPA)**: Kubernetes原生缩放控制器
- **Custom Metrics API**: 自定义指标API服务器
- **Prometheus**: 指标收集和存储
- **ServiceMonitor**: Prometheus服务发现配置

### 2. 缩放指标

#### Backend Pod缩放指标 (权重分配)
| 指标类型 | 指标名称 | 阈值 | 权重 | 说明 |
|---------|----------|------|------|------|
| 资源指标 | CPU使用率 | 70% | 25% | 基础系统负载 |
| 资源指标 | 内存使用率 | 80% | 25% | 内存压力监控 |
| 自定义指标 | 并发用户数 | 50个 | 20% | 实际用户负载 |
| 自定义指标 | 每分钟请求数 | 1000个 | 15% | API调用频率 |
| 自定义指标 | 带宽使用 | 100Mbps | 15% | 网络流量压力 |

#### Frontend Pod缩放指标
| 指标类型 | 指标名称 | 阈值 | 权重 | 说明 |
|---------|----------|------|------|------|
| 资源指标 | CPU使用率 | 75% | 50% | 前端渲染负载 |
| 资源指标 | 内存使用率 | 85% | 50% | 静态资源缓存 |

## ⚙️ 缩放配置

### Backend缩放策略
```yaml
最小副本数: 1
最大副本数: 10
扩容策略:
  - 稳定窗口: 60秒
  - 最大扩容: 100%（翻倍）或2个Pod
  - 策略: 保守（选择最小值）
缩容策略:
  - 稳定窗口: 300秒（5分钟）
  - 最大缩容: 50%或1个Pod
  - 策略: 保守（选择最小值）
```

### Frontend缩放策略
```yaml
最小副本数: 2
最大副本数: 6
扩容策略:
  - 稳定窗口: 60秒
  - 最大扩容: 100%或2个Pod
缩容策略:
  - 稳定窗口: 300秒
  - 最大缩容: 50%或1个Pod
```

## 📊 监控指标详解

### 1. Prometheus指标
应用程序暴露的指标端点：
- **主要指标**: `http://<backend-service>:5000/metrics`
- **缩放指标**: `http://<backend-service>:5000/api/scaling/metrics`

### 2. 自定义指标定义
```
vpn_proxy_concurrent_users      # 当前并发用户数
vpn_proxy_connections_total     # 总连接数
vpn_proxy_requests_per_minute   # 每分钟请求数
vpn_proxy_bandwidth_mbps        # 带宽使用（Mbps）
vpn_proxy_bytes_total           # 总传输字节数
vpn_proxy_running               # 服务运行状态
```

### 3. 告警规则
| 告警名称 | 触发条件 | 持续时间 | 严重级别 |
|---------|----------|----------|----------|
| VPNHighConcurrentUsers | 并发用户 > 40 | 2分钟 | warning |
| VPNHighBandwidthUsage | 带宽使用 > 80Mbps | 2分钟 | warning |
| VPNHighRequestRate | 请求频率 > 800/分钟 | 2分钟 | warning |
| VPNBackendPodCPUHigh | Pod CPU > 70% | 3分钟 | warning |
| VPNBackendPodMemoryHigh | Pod 内存 > 80% | 3分钟 | warning |

## 🚀 部署步骤

### 1. 快速部署（推荐）
```powershell
# Windows PowerShell
cd C:\Users\20399\Desktop\VPN-final\VPN\k8s
.\deploy-autoscaling.ps1 -Action deploy
```

### 2. 手动部署
```bash
# 1. 部署自定义指标API
kubectl apply -f custom-metrics-api.yaml

# 2. 部署Prometheus监控配置
kubectl apply -f prometheus-monitoring.yaml

# 3. 部署HPA配置
kubectl apply -f hpa-backend.yaml
```

### 3. 验证部署
```bash
# 查看HPA状态
kubectl get hpa -n vpn-proxy

# 查看Pod状态
kubectl get pods -n vpn-proxy

# 查看缩放事件
kubectl get events -n vpn-proxy --field-selector reason=SuccessfulRescale

# 测试自定义指标
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/vpn-proxy/services/backend-service/vpn_proxy_concurrent_users"
```

## 🔧 配置调优

### 1. 阈值调整
根据实际业务需求调整缩放阈值：

```yaml
# 修改 hpa-backend.yaml 中的阈值
metrics:
- type: Object
  object:
    metric:
      name: vpn_proxy_concurrent_users
    target:
      type: Value
      value: "50"  # 调整此值
```

### 2. 副本数限制
```yaml
# 修改最大最小副本数
spec:
  minReplicas: 1    # 最小副本数
  maxReplicas: 10   # 最大副本数
```

### 3. 缩放行为调整
```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 60    # 扩容稳定窗口
    policies:
    - type: Percent
      value: 100                      # 扩容百分比
      periodSeconds: 60
  scaleDown:
    stabilizationWindowSeconds: 300   # 缩容稳定窗口
```

## 📈 监控和运维

### 1. 实时监控命令
```bash
# 监控HPA状态
watch kubectl get hpa -n vpn-proxy

# 监控Pod变化
watch kubectl get pods -n vpn-proxy

# 查看指标值
kubectl top pods -n vpn-proxy --custom-metrics

# 查看缩放历史
kubectl describe hpa backend-hpa -n vpn-proxy
```

### 2. 日志查看
```bash
# 查看自定义指标API日志
kubectl logs -l app=custom-metrics-apiserver -n vpn-proxy

# 查看backend pod日志
kubectl logs -l app=vpn-backend -n vpn-proxy

# 查看HPA控制器日志
kubectl logs -n kube-system -l app=kube-controller-manager
```

### 3. 故障排除

#### 常见问题
1. **自定义指标不可用**
   - 检查Prometheus是否正常收集指标
   - 验证ServiceMonitor配置
   - 确认自定义指标API Pod状态

2. **缩放不生效**
   - 检查HPA状态和事件
   - 验证资源请求和限制设置
   - 确认指标数值是否超过阈值

3. **频繁缩放**
   - 调整稳定窗口时间
   - 修改缩放策略为更保守
   - 检查指标波动情况

## 🔐 安全考虑

### 1. RBAC权限
自定义指标API需要以下权限：
- `custom.metrics.k8s.io` API组的所有权限
- 命名空间、Pod、服务的读取权限
- 系统认证授权权限

### 2. TLS证书
- 自定义指标API使用TLS加密通信
- 默认使用自签名证书（测试环境）
- 生产环境建议使用正式CA签发的证书

## 📚 参考资料

- [Kubernetes HPA官方文档](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Prometheus Adapter文档](https://github.com/kubernetes-sigs/prometheus-adapter)
- [Custom Metrics API](https://github.com/kubernetes/community/blob/master/contributors/design-proposals/instrumentation/custom-metrics-api.md)

## 🆘 支持和维护

### 问题反馈
如遇到问题，请收集以下信息：
1. HPA状态输出
2. Pod状态和日志
3. 自定义指标API日志
4. 相关事件记录

### 更新升级
建议定期检查组件版本并进行升级：
- Prometheus Adapter
- Kubernetes版本兼容性
- 监控规则更新
