from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socket
import threading
import select
import requests
import time
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# 配置 CORS
cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"]
if os.getenv('FLASK_ENV') == 'production':
    cors_origins.append("*")  # 生产环境可以配置具体域名

CORS(app, origins=cors_origins)
socketio = SocketIO(app, cors_allowed_origins=cors_origins, async_mode=os.getenv('SOCKETIO_ASYNC_MODE', 'threading'))

# 全局变量存储代理状态
proxy_status = {
    'running': False,
    'port': 8888,
    'connections': 0,
    'total_bytes': 0,
    'active_connections': [],
    'start_time': None
}

proxy_server = None
proxy_thread = None

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.connections = {}
        
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"SOCKS5 proxy server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_sock, addr = self.server_socket.accept()
                    connection_id = f"{addr[0]}:{addr[1]}"
                    self.connections[connection_id] = {
                        'start_time': datetime.now(),
                        'bytes_sent': 0,
                        'bytes_received': 0,
                        'target': None
                    }
                    
                    thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_sock, addr, connection_id),
                        daemon=True
                    )
                    thread.start()
                    
                    # 更新全局状态
                    proxy_status['connections'] = len(self.connections)
                    proxy_status['active_connections'] = list(self.connections.keys())
                    
                    # 发送实时更新到前端
                    socketio.emit('proxy_stats', proxy_status)
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connections: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}")
            raise
            
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("SOCKS5 proxy server stopped")
        
    def handle_client(self, client_sock, addr, connection_id):
        remote = None
        try:
            # SOCKS5 握手
            ver, nmethods = client_sock.recv(2)
            methods = client_sock.recv(nmethods)
            client_sock.sendall(b'\x05\x00')  # 无认证
            
            # 请求阶段
            ver, cmd, _, atyp = client_sock.recv(4)
            
            if atyp == 1:  # IPv4
                addr_bytes = client_sock.recv(4)
                target_addr = socket.inet_ntoa(addr_bytes)
            elif atyp == 3:  # 域名
                domain_len = client_sock.recv(1)[0]
                target_addr = client_sock.recv(domain_len).decode()
            else:
                client_sock.close()
                return
                
            port = int.from_bytes(client_sock.recv(2), 'big')
            
            if cmd != 1:  # 只支持CONNECT
                client_sock.close()
                return
                
            # 连接目标服务器
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(10)
            remote.connect((target_addr, port))
            
            # 更新连接信息
            self.connections[connection_id]['target'] = f"{target_addr}:{port}"
            
            # 回复成功
            reply = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + (8888).to_bytes(2, 'big')
            client_sock.sendall(reply)
            
            # 数据转发
            sockets = [client_sock, remote]
            while self.running:
                try:
                    r, _, _ = select.select(sockets, [], [], 1.0)
                    for s in r:
                        data = s.recv(4096)
                        if not data:
                            return
                            
                        if s is client_sock:
                            remote.sendall(data)
                            self.connections[connection_id]['bytes_sent'] += len(data)
                            proxy_status['total_bytes'] += len(data)
                        else:
                            client_sock.sendall(data)
                            self.connections[connection_id]['bytes_received'] += len(data)
                            proxy_status['total_bytes'] += len(data)
                            
                        # 定期发送统计更新
                        socketio.emit('proxy_stats', proxy_status)
                        
                except Exception as e:
                    logger.error(f"Error in data forwarding: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            if remote:
                remote.close()
            client_sock.close()
            
            # 清理连接记录
            if connection_id in self.connections:
                del self.connections[connection_id]
            proxy_status['connections'] = len(self.connections)
            proxy_status['active_connections'] = list(self.connections.keys())
            socketio.emit('proxy_stats', proxy_status)

# API 路由
@app.route('/api/proxy/status', methods=['GET'])
def get_proxy_status():
    return jsonify(proxy_status)

@app.route('/api/proxy/start', methods=['POST'])
def start_proxy():
    global proxy_server, proxy_thread
    
    if proxy_status['running']:
        return jsonify({'error': 'Proxy is already running'}), 400
        
    try:
        data = request.get_json() or {}
        port = data.get('port', 8888)
        
        proxy_server = ProxyServer(port=port)
        proxy_thread = threading.Thread(target=proxy_server.start, daemon=True)
        proxy_thread.start()
        
        proxy_status['running'] = True
        proxy_status['port'] = port
        proxy_status['start_time'] = datetime.now().isoformat()
        proxy_status['connections'] = 0
        proxy_status['total_bytes'] = 0
        
        return jsonify({'message': 'Proxy started successfully', 'status': proxy_status})
        
    except Exception as e:
        logger.error(f"Failed to start proxy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/stop', methods=['POST'])
def stop_proxy():
    global proxy_server
    
    if not proxy_status['running']:
        return jsonify({'error': 'Proxy is not running'}), 400
        
    try:
        if proxy_server:
            proxy_server.stop()
            
        proxy_status['running'] = False
        proxy_status['start_time'] = None
        proxy_status['connections'] = 0
        proxy_status['active_connections'] = []
        
        return jsonify({'message': 'Proxy stopped successfully', 'status': proxy_status})
        
    except Exception as e:
        logger.error(f"Failed to stop proxy: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/proxy/test', methods=['POST'])
def test_connection():
    data = request.get_json()
    test_url = data.get('url', 'http://httpbin.org/ip')  # 使用httpbin测试IP
    
    try:
        if not proxy_status['running']:
            return jsonify({'success': False, 'error': '代理服务未运行'}), 400
            
        import time
        start_time = time.time()
        
        # 测试SOCKS5代理连接
        try:
            # 创建一个测试socket连接到代理服务器
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(5)
            
            # 连接到本地SOCKS5代理
            test_socket.connect(('127.0.0.1', proxy_status['port']))
            
            # SOCKS5握手
            test_socket.sendall(b'\x05\x01\x00')  # 版本5，1个方法，无认证
            response = test_socket.recv(2)
            
            if len(response) != 2 or response[0] != 5 or response[1] != 0:
                test_socket.close()
                return jsonify({
                    'success': False, 
                    'error': 'SOCKS5握手失败'
                })
            
            # 请求连接到测试目标
            target_host = 'httpbin.org'
            target_port = 80
            
            # 构建SOCKS5连接请求
            request_data = b'\x05\x01\x00\x03'  # 版本、命令(CONNECT)、保留、地址类型(域名)
            request_data += bytes([len(target_host)]) + target_host.encode()  # 域名长度和域名
            request_data += target_port.to_bytes(2, 'big')  # 端口
            
            test_socket.sendall(request_data)
            response = test_socket.recv(10)
            
            if len(response) < 4 or response[0] != 5 or response[1] != 0:
                test_socket.close()
                return jsonify({
                    'success': False, 
                    'error': f'SOCKS5连接请求失败，响应码: {response[1] if len(response) > 1 else "未知"}'
                })
            
            # 发送HTTP请求
            http_request = f"GET /ip HTTP/1.1\r\nHost: {target_host}\r\nConnection: close\r\n\r\n"
            test_socket.sendall(http_request.encode())
            
            # 接收响应
            response_data = b''
            while True:
                chunk = test_socket.recv(1024)
                if not chunk:
                    break
                response_data += chunk
                
            test_socket.close()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            # 解析HTTP响应
            if b'HTTP/1.1 200' in response_data:
                return jsonify({
                    'success': True,
                    'message': f'SOCKS5代理连接测试成功',
                    'response_time': f'{response_time}ms',
                    'target': f'{target_host}:{target_port}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'HTTP请求失败，响应: {response_data[:100].decode("utf-8", errors="ignore")}'
                })
                
        except socket.timeout:
            return jsonify({
                'success': False,
                'error': '连接超时，代理服务可能未正常工作'
            })
        except ConnectionRefusedError:
            return jsonify({
                'success': False,
                'error': f'无法连接到代理端口 {proxy_status["port"]}'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'代理测试失败: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"Test connection error: {e}")
        return jsonify({'success': False, 'error': f'测试失败: {str(e)}'})

@app.route('/api/connections', methods=['GET'])
def get_connections():
    if proxy_server and hasattr(proxy_server, 'connections'):
        return jsonify(proxy_server.connections)
    return jsonify({})

# WebSocket 事件处理
@socketio.on('connect')
def handle_connect():
    emit('proxy_stats', proxy_status)

@socketio.on('disconnect')
def handle_disconnect():
    pass

# 健康检查端点 (用于 Kubernetes)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/ready', methods=['GET'])
def readiness_check():
    return jsonify({'status': 'ready', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
