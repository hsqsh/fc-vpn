# Backend

基于 FastAPI 的后端服务。

## 目录结构
- app/proxy.py      # 代理转发核心逻辑
- app/k8s_mock.py   # K8s 场景模拟接口
- app/config.py     # 配置
- main.py           # 启动入口

## 启动方法
```bash
pip install -r requirements.txt
uvicorn main:app --reload
``` 