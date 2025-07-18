"""
配置管理模块
管理应用配置和环境变量
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # CORS配置
    CORS_ORIGINS = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001"
    ]
    
    # 生产环境CORS配置 - 适配Kubernetes环境
    if FLASK_ENV == 'production':
        # 检查是否在Kubernetes环境中
        if os.getenv('KUBERNETES_SERVICE_HOST'):
            # K8s环境：允许前端服务访问
            frontend_service_url = os.getenv('FRONTEND_SERVICE_URL', 'http://frontend-service')
            CORS_ORIGINS.extend([
                frontend_service_url,
                "http://frontend-service",
                "https://frontend-service"
            ])
        else:
            # 非K8s生产环境：允许所有源（需要根据实际需求配置）
            CORS_ORIGINS.append("*")
    
    # SocketIO配置
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'threading')
    
    # 代理服务器配置 - 适配Kubernetes环境变量
    DEFAULT_PROXY_HOST = '0.0.0.0'
    DEFAULT_PROXY_PORT = int(os.getenv('PROXY_PORT', '8888'))  # 从K8s环境变量读取
    DEFAULT_PROXY_TYPE = 'http'
    
    # Flask API服务器端口配置 - 适配Kubernetes环境变量  
    FLASK_API_PORT = int(os.getenv('PORT', '5000'))  # 从K8s环境变量读取
    
    # Redis配置 - 适配Kubernetes环境变量
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 监控配置
    STATS_BROADCAST_INTERVAL = 2  # 秒
    CONNECTION_TIMEOUT = 10  # 秒
    
    @classmethod
    def get_proxy_config(cls):
        """获取代理配置"""
        return {
            'host': cls.DEFAULT_PROXY_HOST,
            'port': cls.DEFAULT_PROXY_PORT,
            'type': cls.DEFAULT_PROXY_TYPE
        }
    
    @classmethod
    def get_cors_config(cls):
        """获取CORS配置"""
        return {
            'origins': cls.CORS_ORIGINS
        }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    DEFAULT_PROXY_PORT = 9999  # 测试时使用不同端口

# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(env_name=None):
    """
    获取配置类
    
    Args:
        env_name: 环境名称
        
    Returns:
        配置类
    """
    if env_name is None:
        env_name = os.getenv('FLASK_ENV', 'development')
    
    return config_map.get(env_name, config_map['default'])
