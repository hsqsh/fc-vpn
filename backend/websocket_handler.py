"""
WebSocket事件处理模块
处理实时通信和状态广播
"""

import logging
from flask_socketio import emit
import threading
import time

logger = logging.getLogger(__name__)

class SocketIOHandler:
    """WebSocket事件处理类"""
    
    def __init__(self, socketio, proxy_status):
        """
        初始化WebSocket处理器
        
        Args:
            socketio: SocketIO实例
            proxy_status: 代理状态字典
        """
        self.socketio = socketio
        self.proxy_status = proxy_status
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # 注册事件处理器
        self.register_handlers()
    
    def register_handlers(self):
        """注册WebSocket事件处理器"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接事件"""
            logger.info('Client connected')
            # 发送当前状态
            emit('proxy_stats', self.proxy_status)
            
            # 启动监控线程（如果还没启动）
            if not self.monitoring_active:
                self.start_monitoring()
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开连接事件"""
            logger.info('Client disconnected')
        
        @self.socketio.on('request_stats')
        def handle_request_stats():
            """客户端请求状态更新"""
            emit('proxy_stats', self.proxy_status)
    
    def start_monitoring(self):
        """启动实时监控线程"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info('Started real-time monitoring thread')
    
    def stop_monitoring(self):
        """停止实时监控"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        logger.info('Stopped real-time monitoring thread')
    
    def _monitoring_loop(self):
        """监控循环 - 定期广播状态更新"""
        while self.monitoring_active:
            try:
                # 每2秒广播一次状态
                self.socketio.emit('proxy_stats', self.proxy_status)
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # 出错时等待更长时间
    
    def broadcast_stats(self, stats=None):
        """
        广播统计信息
        
        Args:
            stats: 要广播的统计信息，默认使用当前proxy_status
        """
        try:
            data = stats if stats else self.proxy_status
            self.socketio.emit('proxy_stats', data)
        except Exception as e:
            logger.error(f"Error broadcasting stats: {e}")
    
    def broadcast_connection_update(self, connection_info):
        """
        广播连接更新
        
        Args:
            connection_info: 连接信息
        """
        try:
            self.socketio.emit('connection_update', connection_info)
        except Exception as e:
            logger.error(f"Error broadcasting connection update: {e}")
    
    def broadcast_traffic_update(self, traffic_data):
        """
        广播流量更新
        
        Args:
            traffic_data: 流量数据
        """
        try:
            self.socketio.emit('traffic_update', traffic_data)
        except Exception as e:
            logger.error(f"Error broadcasting traffic update: {e}")
