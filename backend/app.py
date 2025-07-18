"""
主应用模块
整合所有后端组件，创建Flask应用
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
import threading
import time
import os

from config import get_config
from api_routes import ProxyAPI
from websocket_handler import SocketIOHandler

class ProxyApp:
    """代理应用主类"""
    
    def __init__(self, config_name='development'):
        """
        初始化应用
        
        Args:
            config_name: 配置环境名称
        """
        self.config = get_config(config_name)
        self.app = None
        self.socketio = None
        self.proxy_api = None
        self.websocket_handler = None
        
        # 全局代理状态 - 增加更多指标
        self.proxy_status = {
            'running': False,
            'port': self.config.DEFAULT_PROXY_PORT,
            'proxy_type': self.config.DEFAULT_PROXY_TYPE,
            'connections': 0,
            'total_bytes': 0,
            'active_connections': [],
            'start_time': None,
            # 新增动态缩放指标
            'concurrent_users': 0,           # 并发用户数
            'requests_per_minute': 0,        # 每分钟请求数
            'bandwidth_usage_mbps': 0.0,     # 带宽使用（Mbps）
            'cpu_usage_percent': 0.0,        # CPU使用率
            'memory_usage_mb': 0.0,          # 内存使用（MB）
        }
        
        # 指标收集
        self.metrics_history = {
            'requests': [],      # 请求历史
            'bandwidth': [],     # 带宽历史
            'connections': [],   # 连接历史
        }
        
        self._setup_app()
        self._setup_logging()
    
    def _setup_app(self):
        """设置Flask应用"""
        self.app = Flask(__name__)
        self.app.config.from_object(self.config)
        
        # 配置CORS
        cors_config = self.config.get_cors_config()
        CORS(self.app, origins=cors_config['origins'])
        
        # 配置SocketIO
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins=cors_config['origins'],
            async_mode=self.config.SOCKETIO_ASYNC_MODE
        )
        
        # 初始化API和WebSocket处理器
        self.proxy_api = ProxyAPI(self.app, self.proxy_status, self.socketio)
        self.websocket_handler = SocketIOHandler(self.socketio, self.proxy_status)
        
        # 添加指标暴露路由
        self._setup_metrics_routes()
        
        # 启动监控线程
        self._start_monitoring()
        
        # 在生产环境中自动启动代理服务
        if self.config.FLASK_ENV == 'production':
            self._auto_start_proxy_service()
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Application initialized with {self.config.__class__.__name__}")
    
    def _start_monitoring(self):
        """启动监控线程"""
        def monitoring_loop():
            """监控循环"""
            while True:
                try:
                    # 更新代理状态
                    if self.proxy_api and self.proxy_api.proxy_server:
                        self.proxy_api.update_proxy_status()
                    
                    # 更新缩放指标
                    self.update_scaling_metrics()
                    
                    time.sleep(self.config.STATS_BROADCAST_INTERVAL)
                    
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def _auto_start_proxy_service(self):
        """在生产环境中自动启动代理服务"""
        def start_proxy_delayed():
            """延迟启动代理服务，等待Flask应用完全初始化"""
            import time
            time.sleep(2)  # 等待Flask应用完全启动
            
            try:
                from proxy_server import ProxyServer
                
                logger = logging.getLogger(__name__)
                logger.info("自动启动代理服务...")
                
                # 获取代理配置
                proxy_config = self.config.get_proxy_config()
                
                # 创建代理服务器实例
                proxy_server = ProxyServer(
                    host=proxy_config['host'],
                    port=proxy_config['port'],
                    proxy_type=proxy_config['type']
                )
                
                # 将代理服务器实例赋值给API处理器
                self.proxy_api.proxy_server = proxy_server
                
                # 启动代理服务器
                proxy_server.start()
                
                # 更新代理状态
                self.proxy_status.update({
                    'running': True,
                    'port': proxy_server.get_actual_port(),
                    'proxy_type': proxy_config['type'],
                    'start_time': time.time(),
                    'connections': 0,
                    'total_bytes': 0,
                    'auto_started': True
                })
                
                logger.info(f"代理服务自动启动成功，端口: {proxy_server.get_actual_port()}")
                
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"自动启动代理服务失败: {e}")
                # 在K8s环境中，如果代理服务启动失败，应该让容器失败
                if os.getenv('KUBERNETES_SERVICE_HOST'):
                    raise
        
        # 在后台线程中启动代理服务
        proxy_startup_thread = threading.Thread(target=start_proxy_delayed, daemon=True)
        proxy_startup_thread.start()
    
    def _setup_metrics_routes(self):
        """设置指标暴露路由"""
        
        @self.app.route('/metrics', methods=['GET'])
        def prometheus_metrics():
            """Prometheus格式的指标暴露"""
            return self.get_prometheus_metrics()
        
        @self.app.route('/api/scaling/metrics', methods=['GET'])
        def scaling_metrics():
            """用于HPA的自定义指标"""
            return jsonify(self.get_scaling_metrics())
        
        @self.app.route('/api/scaling/health', methods=['GET'])
        def scaling_health():
            """缩放健康检查"""
            return jsonify({
                'status': 'healthy',
                'pod_name': os.getenv('HOSTNAME', 'unknown'),
                'timestamp': time.time(),
                'ready_for_scaling': True
            })
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Kubernetes liveness probe健康检查"""
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'vpn-backend'
            })
        
        @self.app.route('/ready', methods=['GET'])
        def readiness_check():
            """Kubernetes readiness probe就绪检查"""
            # 检查关键服务是否就绪
            is_ready = True
            checks = {}
            
            # 检查Redis连接
            try:
                redis_url = self.config.REDIS_URL
                if redis_url and 'redis' in redis_url.lower():
                    checks['redis'] = 'ok'
                else:
                    checks['redis'] = 'not_configured'
            except Exception as e:
                checks['redis'] = f'error: {str(e)}'
                is_ready = False
            
            # 检查代理服务 - 在生产环境中检查端口是否实际监听
            if self.config.FLASK_ENV == 'production':
                import socket
                proxy_port = int(self.config.DEFAULT_PROXY_PORT)
                try:
                    # 检查代理端口是否可用
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', proxy_port))
                    sock.close()
                    
                    if result == 0:
                        checks['proxy_service'] = 'running'
                    else:
                        # 检查是否有其他端口在运行(8889等)
                        for alt_port in [proxy_port + 1, proxy_port + 2]:
                            sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock2.settimeout(1)
                            alt_result = sock2.connect_ex(('localhost', alt_port))
                            sock2.close()
                            if alt_result == 0:
                                checks['proxy_service'] = f'running_on_port_{alt_port}'
                                break
                        else:
                            checks['proxy_service'] = 'not_running'
                            is_ready = False
                except Exception as e:
                    checks['proxy_service'] = f'error: {str(e)}'
                    is_ready = False
            else:
                # 开发环境中代理服务可选
                checks['proxy_service'] = 'ok'
            
            # 检查Flask应用状态
            checks['flask_app'] = 'ok'
            
            # 检查环境配置
            checks['environment'] = self.config.FLASK_ENV
            checks['kubernetes'] = 'yes' if os.getenv('KUBERNETES_SERVICE_HOST') else 'no'
            
            return jsonify({
                'status': 'ready' if is_ready else 'not_ready',
                'checks': checks,
                'timestamp': time.time(),
                'pod_name': os.getenv('HOSTNAME', 'unknown')
            }), 200 if is_ready else 503
    
    def get_prometheus_metrics(self):
        """生成Prometheus格式的指标"""
        metrics = []
        
        # 连接数指标
        metrics.append(f'vpn_proxy_connections_total {self.proxy_status["connections"]}')
        
        # 流量指标
        metrics.append(f'vpn_proxy_bytes_total {self.proxy_status["total_bytes"]}')
        
        # 并发用户数
        metrics.append(f'vpn_proxy_concurrent_users {self.proxy_status["concurrent_users"]}')
        
        # 每分钟请求数
        metrics.append(f'vpn_proxy_requests_per_minute {self.proxy_status["requests_per_minute"]}')
        
        # 带宽使用
        metrics.append(f'vpn_proxy_bandwidth_mbps {self.proxy_status["bandwidth_usage_mbps"]}')
        
        # 服务状态
        metrics.append(f'vpn_proxy_running {1 if self.proxy_status["running"] else 0}')
        
        return '\n'.join(metrics) + '\n'
    
    def get_scaling_metrics(self):
        """获取用于动态缩放的指标"""
        return {
            'concurrent_users': self.proxy_status['concurrent_users'],
            'connections_total': self.proxy_status['connections'],
            'requests_per_minute': self.proxy_status['requests_per_minute'],
            'bandwidth_mbps': self.proxy_status['bandwidth_usage_mbps'],
            'total_bytes': self.proxy_status['total_bytes'],
            'cpu_usage_percent': self.proxy_status['cpu_usage_percent'],
            'memory_usage_mb': self.proxy_status['memory_usage_mb'],
            'load_score': self._calculate_load_score(),
            'timestamp': time.time(),
            'pod_name': os.getenv('HOSTNAME', 'unknown')
        }
    
    def _calculate_load_score(self):
        """计算负载评分 (0-100)"""
        # 综合考虑多个指标的负载评分
        connection_score = min(self.proxy_status['connections'] / 100 * 50, 50)  # 连接数权重50%
        bandwidth_score = min(self.proxy_status['bandwidth_usage_mbps'] / 100 * 30, 30)  # 带宽权重30%
        user_score = min(self.proxy_status['concurrent_users'] / 50 * 20, 20)  # 用户数权重20%
        
        total_score = connection_score + bandwidth_score + user_score
        return min(total_score, 100.0)
    
    def update_scaling_metrics(self):
        """更新缩放相关指标"""
        current_time = time.time()
        
        # 更新并发用户数（基于活跃连接）
        if self.proxy_api and self.proxy_api.proxy_server:
            connections_stats = self.proxy_api.proxy_server.get_connections_stats()
            self.proxy_status['connections'] = connections_stats['total_connections']
            self.proxy_status['total_bytes'] = connections_stats['total_bytes']
            
            # 计算并发用户数（基于唯一IP）
            unique_ips = set()
            for conn in connections_stats.get('active_connections', []):
                if 'id' in conn:
                    ip = conn['id'].split(':')[0]
                    unique_ips.add(ip)
            self.proxy_status['concurrent_users'] = len(unique_ips)
        
        # 计算每分钟请求数
        self.metrics_history['requests'].append({
            'timestamp': current_time,
            'count': self.proxy_status['connections']
        })
        
        # 保留最近1分钟的数据
        minute_ago = current_time - 60
        self.metrics_history['requests'] = [
            r for r in self.metrics_history['requests']
            if r['timestamp'] > minute_ago
        ]
        
        # 计算每分钟请求数
        if len(self.metrics_history['requests']) > 1:
            self.proxy_status['requests_per_minute'] = len(self.metrics_history['requests'])
        
        # 计算带宽使用（基于字节传输）
        self.metrics_history['bandwidth'].append({
            'timestamp': current_time,
            'bytes': self.proxy_status['total_bytes']
        })
        
        # 保留最近1分钟的数据
        self.metrics_history['bandwidth'] = [
            b for b in self.metrics_history['bandwidth'] 
            if b['timestamp'] > minute_ago
        ]
        
        # 计算带宽（Mbps）
        if len(self.metrics_history['bandwidth']) > 1:
            bytes_diff = (self.metrics_history['bandwidth'][-1]['bytes'] - 
                         self.metrics_history['bandwidth'][0]['bytes'])
            time_diff = (self.metrics_history['bandwidth'][-1]['timestamp'] - 
                        self.metrics_history['bandwidth'][0]['timestamp'])
            if time_diff > 0:
                # 转换为Mbps
                self.proxy_status['bandwidth_usage_mbps'] = (bytes_diff * 8) / (time_diff * 1000000)

    def get_app(self):
        """获取Flask应用实例"""
        return self.app
    
    def get_socketio(self):
        """获取SocketIO实例"""
        return self.socketio
    
    def run(self, host='0.0.0.0', port=None, debug=None):
        """
        运行应用
        
        Args:
            host: 监听地址
            port: 监听端口 (优先使用环境变量PORT或config中的FLASK_API_PORT)
            debug: 调试模式
        """
        if port is None:
            port = self.config.FLASK_API_PORT
        if debug is None:
            debug = self.config.DEBUG
            
        logger = logging.getLogger(__name__)
        logger.info(f"Starting proxy application on {host}:{port}")
        logger.info(f"Proxy service will run on port {self.config.DEFAULT_PROXY_PORT}")
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

# 便捷函数
def create_app(config_name='development'):
    """
    创建应用工厂函数
    
    Args:
        config_name: 配置环境名称
        
    Returns:
        ProxyApp实例
    """
    return ProxyApp(config_name)

# 创建全局应用实例供Gunicorn使用
config_name = os.getenv('FLASK_ENV', 'production')
proxy_app_instance = create_app(config_name)
app = proxy_app_instance.get_app()

if __name__ == '__main__':
    # 检查运行环境
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # 生产环境：读取环境变量配置
        prod_app = create_app('production')
        port = int(os.getenv('PORT', '5000'))
        prod_app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # 开发环境
        dev_app = create_app('development')
        dev_app.run(debug=True)
