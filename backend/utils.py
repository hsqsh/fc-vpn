"""
工具函数模块
提供常用的工具函数
"""

import socket
import time
import json
from datetime import datetime
from urllib.parse import urlparse

def format_bytes(bytes_count):
    """
    格式化字节数显示
    
    Args:
        bytes_count (int): 字节数
        
    Returns:
        str: 格式化后的字符串
    """
    if bytes_count == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    k = 1024
    i = 0
    
    while bytes_count >= k and i < len(units) - 1:
        bytes_count /= k
        i += 1
    
    return f"{bytes_count:.2f} {units[i]}"

def format_duration(seconds):
    """
    格式化时间间隔
    
    Args:
        seconds (int): 秒数
        
    Returns:
        str: 格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}小时{minutes}分{secs}秒"

def validate_url(url):
    """
    验证URL格式
    
    Args:
        url (str): 要验证的URL
        
    Returns:
        tuple: (is_valid, parsed_url, error_message)
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        parsed = urlparse(url)
        
        if not parsed.hostname:
            return False, None, "无效的主机名"
        
        return True, parsed, None
        
    except Exception as e:
        return False, None, f"URL解析错误: {str(e)}"

def check_port_availability(host, port):
    """
    检查端口是否可用
    
    Args:
        host (str): 主机地址
        port (int): 端口号
        
    Returns:
        bool: 端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # 0表示连接成功，即端口被占用
    except Exception:
        return False

def get_local_ip():
    """
    获取本机IP地址
    
    Returns:
        str: 本机IP地址
    """
    try:
        # 创建一个UDP socket，连接到远程地址，获取本地IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
            return local_ip
    except Exception:
        return "127.0.0.1"

def create_response_dict(success=True, message="", data=None, error=None):
    """
    创建统一的API响应格式
    
    Args:
        success (bool): 是否成功
        message (str): 响应消息
        data: 响应数据
        error (str): 错误信息
        
    Returns:
        dict: 响应字典
    """
    response = {
        'success': success,
        'timestamp': time.time(),
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response

def log_connection_event(event_type, connection_id, details=None):
    """
    记录连接事件日志
    
    Args:
        event_type (str): 事件类型 ('connect', 'disconnect', 'data')
        connection_id (str): 连接ID
        details (dict): 详细信息
    """
    import logging
    logger = logging.getLogger(__name__)
    
    log_data = {
        'event': event_type,
        'connection_id': connection_id,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    logger.info(f"Connection event: {json.dumps(log_data)}")

def safe_json_loads(json_str, default=None):
    """
    安全的JSON解析
    
    Args:
        json_str (str): JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析结果或默认值
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, max_requests=100, time_window=60):
        """
        初始化速率限制器
        
        Args:
            max_requests (int): 时间窗口内最大请求数
            time_window (int): 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, client_id):
        """
        检查客户端是否允许请求
        
        Args:
            client_id (str): 客户端ID
            
        Returns:
            bool: 是否允许
        """
        now = time.time()
        
        # 清理过期记录
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.time_window
            ]
        else:
            self.requests[client_id] = []
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[client_id].append(now)
        return True

class ConnectionPool:
    """简单的连接池管理"""
    
    def __init__(self, max_connections=100):
        """
        初始化连接池
        
        Args:
            max_connections (int): 最大连接数
        """
        self.max_connections = max_connections
        self.active_connections = {}
        self.connection_count = 0
    
    def add_connection(self, connection_id, connection_info):
        """
        添加连接
        
        Args:
            connection_id (str): 连接ID
            connection_info (dict): 连接信息
            
        Returns:
            bool: 是否添加成功
        """
        if self.connection_count >= self.max_connections:
            return False
        
        self.active_connections[connection_id] = connection_info
        self.connection_count += 1
        return True
    
    def remove_connection(self, connection_id):
        """
        移除连接
        
        Args:
            connection_id (str): 连接ID
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            self.connection_count -= 1
    
    def get_connection_stats(self):
        """
        获取连接统计
        
        Returns:
            dict: 连接统计信息
        """
        return {
            'total_connections': self.connection_count,
            'max_connections': self.max_connections,
            'utilization': (self.connection_count / self.max_connections) * 100,
            'active_connections': list(self.active_connections.keys())
        }
