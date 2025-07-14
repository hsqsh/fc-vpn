from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import requests

router = APIRouter()

# 从环境变量中获取 Go 后端 URL，默认本地调试用 localhost:8080
GO_BACKEND_URL = os.getenv("GO_BACKEND_URL", "http://localhost:8080")

def proxy_to_go(path: str):
    """
    通用转发函数：把请求转发到 Go 后端
    """
    try:
        url = f"{GO_BACKEND_URL}{path}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return JSONResponse(content=resp.json())
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/k8s/pods")
def list_pods():
    return proxy_to_go("/k8s/pods")

@router.get("/k8s/nodes")
def list_nodes():
    return proxy_to_go("/k8s/nodes")
