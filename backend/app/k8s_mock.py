# 使用 fastapi K8s 场景的模拟接口
from fastapi import APIRouter

router = APIRouter()

@router.get("/k8s/pods")
def list_pods():
    # 返回模拟的 pod 列表
    return {
        "pods": [
            {"name": "vpn-proxy-1", "status": "Running", "ip": "10.0.0.1"},
            {"name": "vpn-proxy-2", "status": "Pending", "ip": "10.0.0.2"},
        ]
    }

@router.get("/k8s/nodes")
def list_nodes():
    # 返回模拟的 node 列表
    return {
        "nodes": [
            {"name": "node-1", "status": "Ready"},
            {"name": "node-2", "status": "NotReady"},
        ]
    }