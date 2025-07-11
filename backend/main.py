from fastapi import FastAPI
from app.proxy import router as proxy_router  # 需要在 proxy.py 中定义 router
from app.k8s_mock import router as k8s_router  # 需要在 k8s_mock.py 中定义 router

app = FastAPI()

# 注册路由
# TODO: 在 proxy.py 和 k8s_mock.py 中定义 router 并实现接口
app.include_router(proxy_router)
app.include_router(k8s_router)

# 启动命令：uvicorn backend.main:app --reload 