# 使用 fastapi K8s 场景的模拟接口
from fastapi import APIRouter
from kubernetes import client, config
import requests
import os

router = APIRouter()

@router.get("/api/cluster-monitor")
def cluster_monitor():
    try:
        # 1. 加载 in-cluster 配置（确保后端部署在 K8s 集群内）
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        namespace = os.environ.get("NAMESPACE", "babelnet")  # 使用 babelnet namespace

        # 2. 获取 Pod 列表
        pods = v1.list_namespaced_pod(namespace=namespace)
        pod_names = [pod.metadata.name for pod in pods.items]

        # 3. 获取 metrics-server 的 Pod 资源使用率
        # 使用 kubectl proxy 风格的 API 调用
        try:
            # 先尝试直接调用 metrics API
            metrics_api = client.CustomObjectsApi()
            metrics = metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            pod_metrics = {}
            for item in metrics.get("items", []):
                name = item["metadata"]["name"]
                containers = item["containers"]
                cpu = sum([parse_cpu(c["usage"]["cpu"]) for c in containers])
                memory = sum([parse_memory(c["usage"]["memory"]) for c in containers])
                pod_metrics[name] = {"cpu": cpu, "memory": memory}
                
        except Exception as e:
            # 如果 metrics API 失败，返回基本 Pod 信息
            pod_metrics = {}
            print(f"Metrics API error: {e}")

        # 4. 组装返回数据
        result = []
        for pod in pods.items:
            name = pod.metadata.name
            result.append({
                "name": name,
                "cpu": pod_metrics.get(name, {}).get("cpu", 0),
                "memory": pod_metrics.get(name, {}).get("memory", 0),
                "status": pod.status.phase
            })

        return {
            "pod_count": len(result),
            "pods": result
        }
        
    except Exception as e:
        return {"error": f"Failed to fetch cluster info: {str(e)}"}

def parse_cpu(cpu_str):
    # 解析 cpu 字符串（如 '10m', '100n', '1'）
    if cpu_str.endswith('n'):
        return float(cpu_str[:-1]) / 1e6  # 转成 m
    if cpu_str.endswith('m'):
        return float(cpu_str[:-1])
    return float(cpu_str) * 1000  # 1 core = 1000m

def parse_memory(mem_str):
    # 解析 memory 字符串（如 '128974848Ki', '129Mi'）
    units = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4}
    for u, v in units.items():
        if mem_str.endswith(u):
            return int(float(mem_str[:-len(u)]) * v)
    return int(mem_str)

# @router.get("/k8s/pods")
# def list_pods():
#     # 返回模拟的 pod 列表
#     return {
#         "pods": [
#             {"name": "vpn-proxy-1", "status": "Running", "ip": "10.0.0.1"},
#             {"name": "vpn-proxy-2", "status": "Pending", "ip": "10.0.0.2"},
#         ]
#     }

# @router.get("/k8s/nodes")
# def list_nodes():
#     # 返回模拟的 node 列表
#     return {
#         "nodes": [
#             {"name": "node-1", "status": "Ready"},
#             {"name": "node-2", "status": "NotReady"},
#         ]
#     }