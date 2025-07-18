# gunicorn.conf.py
# Gunicorn configuration for production deployment

import os
import multiprocessing

# 服务器套接字配置
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker进程配置
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "eventlet"  # 支持WebSocket
worker_connections = 1000
timeout = 30
keepalive = 2

# 进程管理
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# 日志配置
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程标识
proc_name = 'vpn-backend'

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 性能调优
sendfile = True
chdir = '/app'

# 开发模式配置
if os.getenv('FLASK_ENV') == 'development':
    reload = True
    workers = 1
    loglevel = 'debug'
