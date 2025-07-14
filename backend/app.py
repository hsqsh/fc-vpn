from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import time

app = FastAPI()

class ProxyTestRequest(BaseModel):
    target_url: str

@app.post("/api/proxy-test")
async def proxy_test(req: ProxyTestRequest, request: Request):
    proxy_url = "socks5://127.0.0.1:1080"
    start = time.time()
    try:
        async with httpx.AsyncClient(proxies=proxy_url, timeout=10) as client:
            r = await client.get(req.target_url)
            elapsed = int((time.time() - start) * 1000)
            # 这里 connection_count 用 1 模拟，实际可根据代理实现统计
            return {
                "status": "success" if r.status_code == 200 else "fail",
                "http_code": r.status_code,
                "response_time_ms": elapsed,
                "traffic_bytes": len(r.content),
                "connection_count": 1
            }
    except Exception as e:
        return {
            "status": "error",
            "http_code": '-',
            "response_time_ms": '-',
            "traffic_bytes": '-',
            "connection_count": '-',
            "error": str(e)
        } 