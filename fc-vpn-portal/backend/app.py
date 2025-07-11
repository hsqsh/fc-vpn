import os
import socket
import threading
import select
import time
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import urlparse

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置 JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-in-production"  # 实际应用中应该使用环境变量
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vpn_service.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 定义数据库模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    account_balance = db.Column(db.Float, default=10.0)  # 新用户默认赠送 $10
    
    def __repr__(self):
        return f'<User {self.username}>'

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target_url = db.Column(db.String(200), nullable=False)
    proxy_port = db.Column(db.Integer, nullable=True)  # 代理服务器端口
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="processing")  # 状态可以是 processing, completed, failed
    cost = db.Column(db.Float, default=0.1)  # 每次请求消费 $0.1
    
    def __repr__(self):
        return f'<ServiceRequest {self.service_id}>'

# 模拟 Kubernetes Operator 交互和代理服务器管理
class ProxyServer:
    def __init__(self, port, target_url):
        self.port = port
        self.target_url = target_url
        self.is_running = False
        self.server_socket = None
        self.thread = None
        self.traffic_stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'connections_total': 0,
            'connections_active': 0,
            'start_time': time.time(),
            'last_activity': time.time()
        }
    
    def start(self):
        """启动代理服务器"""
        if self.is_running:
            return
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(5)
            self.is_running = True
              # 在单独的线程中运行代理服务器
            self.thread = threading.Thread(target=self._run_proxy, daemon=True)
            self.thread.start()
            
            print(f"[PROXY] Started proxy server on port {self.port} for {self.target_url}")
            return True
        except Exception as e:
            print(f"[PROXY] Failed to start proxy on port {self.port}: {e}")
            return False
    
    def _run_proxy(self):
        """运行代理服务器主循环"""
        while self.is_running:
            try:
                client_sock, addr = self.server_socket.accept()
                # 为每个客户端连接创建新线程
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception as e:
                if self.is_running:  # 只有在服务器应该运行时才打印错误
                    print(f"[PROXY] Error accepting connection: {e}")
                break
    
    def _handle_client(self, client_sock):
        """处理客户端连接"""
        self.traffic_stats['connections_total'] += 1
        self.traffic_stats['connections_active'] += 1
        self.traffic_stats['last_activity'] = time.time()
        
        try:
            # 简化的HTTP代理实现
            request_data = client_sock.recv(4096).decode('utf-8')
            if not request_data:
                return
            
            # 更新接收字节数
            self.traffic_stats['bytes_received'] += len(request_data.encode('utf-8'))
            
            # 解析HTTP请求
            lines = request_data.split('\n')
            if lines:
                request_line = lines[0]
                if 'GET' in request_line:                    # 直接转发到目标URL
                    parsed_url = urlparse(self.target_url)
                    target_host = parsed_url.netloc or parsed_url.path
                    target_port = 80 if parsed_url.scheme == 'http' else 443
                    
                    # 简单的HTTP响应，重定向到目标URL
                    response = f"""HTTP/1.1 302 Found\r
Location: {self.target_url}\r
Content-Type: text/html\r
Content-Length: 0\r
\r
"""
                    # 更新发送字节数
                    response_bytes = response.encode()
                    self.traffic_stats['bytes_sent'] += len(response_bytes)
                    
                    client_sock.send(response_bytes)
                    print(f"[PROXY] Redirected client to {self.target_url}")
        
        except Exception as e:
            print(f"[PROXY] Error handling client: {e}")
        finally:
            self.traffic_stats['connections_active'] -= 1
            try:
                client_sock.close()
            except:
                pass
    
    def get_traffic_stats(self):
        """获取流量统计信息"""
        current_time = time.time()
        uptime = current_time - self.traffic_stats['start_time']
        
        return {
            'port': self.port,
            'target_url': self.target_url,
            'is_running': self.is_running,
            'uptime_seconds': int(uptime),
            'bytes_sent': self.traffic_stats['bytes_sent'],
            'bytes_received': self.traffic_stats['bytes_received'],
            'connections_total': self.traffic_stats['connections_total'],
            'connections_active': self.traffic_stats['connections_active'],
            'last_activity': self.traffic_stats['last_activity'],
            'avg_connections_per_minute': self.traffic_stats['connections_total'] / (uptime / 60) if uptime > 0 else 0
        }
    
    def stop(self):
        """停止代理服务器"""
        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print(f"[PROXY] Stopped proxy server on port {self.port}")

class MockK8sOperatorClient:
    def __init__(self):
        self.active_proxies = {}  # service_id -> ProxyServer
        self.port_counter = 9000  # 起始端口号
    
    def create_access_policy(self, username, target_url):
        """创建访问策略并启动代理服务器"""
        service_id = "service_" + datetime.now().strftime("%Y%m%d%H%M%S") + "_" + username
        
        # 分配一个新的端口
        proxy_port = self.port_counter
        self.port_counter += 1
        
        # 创建并启动代理服务器
        proxy = ProxyServer(proxy_port, target_url)
        if proxy.start():
            self.active_proxies[service_id] = proxy
            
            print(f"[MOCK K8S] Created AccessPolicy for user '{username}' to target '{target_url}'")
            print(f"[MOCK K8S] Proxy server started on port {proxy_port}")
            
            return True, service_id, proxy_port
        else:
            return False, None, None
    
    def delete_access_policy(self, service_id):
        """删除访问策略并停止代理服务器"""
        if service_id in self.active_proxies:
            proxy = self.active_proxies[service_id]
            proxy.stop()
            del self.active_proxies[service_id]
            print(f"[MOCK K8S] Deleted AccessPolicy for service {service_id}")
            return True
        return False

# 全局K8s客户端实例
k8s_client = MockK8sOperatorClient()

# 创建数据库表
with app.app_context():
    # For development: drop the database if it exists to ensure schema is up to date
    db_path = os.path.join(app.instance_path, 'vpn_service.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed old database at {db_path}")
        except OSError as e:
            print(f"Error removing database file {db_path}: {e}")
    
    db.create_all()

# 注册路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    
    # 检查用户是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    
    # 创建新用户
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        email=data.get('email', None),
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"message": "Missing username or password"}), 400
    
    # 查找用户
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"message": "Invalid username or password"}), 401
    
    # 生成访问令牌
    access_token = create_access_token(identity=user.username)
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200

@app.route('/api/service/request', methods=['POST'])
@jwt_required()
def request_service():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'target_url' not in data:
        return jsonify({"message": "Missing target URL"}), 400
    
    target_url = data['target_url']
    
    # 验证URL格式
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url
    
    # 获取当前用户
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # 检查账户余额
    if user.account_balance < 0.1:  # 每次请求消费 $0.1
        return jsonify({"message": "Insufficient balance"}), 400
    
    # 使用全局K8s客户端创建代理
    success, service_id, proxy_port = k8s_client.create_access_policy(current_user, target_url)
    
    if not success:
        return jsonify({"message": "Failed to create service request"}), 500
    
    # 记录服务请求并扣费
    service_request = ServiceRequest(
        service_id=service_id,
        user_id=user.id,
        target_url=target_url,
        proxy_port=proxy_port,
        status="completed"  # 代理已启动，标记为完成
    )
    
    user.account_balance -= 0.1  # 扣费
    
    db.session.add(service_request)
    db.session.commit()
      # 构造代理URL
    proxy_url = f"http://localhost:{proxy_port}"
    
    return jsonify({
        "message": "VPN service request received and proxy is ready.",
        "service_id": service_id,
        "proxy_url": proxy_url,
        "target_url": target_url
    }), 200

@app.route('/api/service/disconnect', methods=['POST'])
@jwt_required()
def disconnect_service():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'service_id' not in data:
        return jsonify({"message": "Missing service ID"}), 400
    
    service_id = data['service_id']
    
    # 验证服务请求是否属于当前用户
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    service_request = ServiceRequest.query.filter_by(
        service_id=service_id, 
        user_id=user.id
    ).first()
    
    if not service_request:
        return jsonify({"message": "Service not found"}), 404
    
    # 停止代理服务器
    success = k8s_client.delete_access_policy(service_id)
    
    if success:
        # 更新服务状态为已断开
        service_request.status = "disconnected"
        db.session.commit()
        
        return jsonify({
            "message": "Service disconnected successfully",
            "service_id": service_id
        }), 200
    else:
        return jsonify({"message": "Failed to disconnect service"}), 500

@app.route('/api/service/monitor', methods=['GET'])
@jwt_required()
def get_monitoring_data():
    """获取实时流量监控数据"""
    current_user = get_jwt_identity()
    
    # 获取当前用户
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # 获取用户的活跃服务请求
    active_services = ServiceRequest.query.filter_by(
        user_id=user.id,
        status="completed"  # 只获取已完成（运行中）的服务
    ).all()
    
    monitoring_data = {
        'user': current_user,
        'timestamp': datetime.utcnow().isoformat(),
        'services': [],
        'summary': {
            'total_services': len(active_services),
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'total_connections': 0,
            'active_connections': 0
        }
    }
    
    # 收集每个服务的流量数据
    for service in active_services:
        if service.service_id in k8s_client.active_proxies:
            proxy = k8s_client.active_proxies[service.service_id]
            stats = proxy.get_traffic_stats()
            
            monitoring_data['services'].append({
                'service_id': service.service_id,
                'target_url': service.target_url,
                'created_at': service.timestamp.isoformat(),
                'stats': stats
            })
            
            # 累计总计数据
            monitoring_data['summary']['total_bytes_sent'] += stats['bytes_sent']
            monitoring_data['summary']['total_bytes_received'] += stats['bytes_received']
            monitoring_data['summary']['total_connections'] += stats['connections_total']
            monitoring_data['summary']['active_connections'] += stats['connections_active']
    
    return jsonify(monitoring_data), 200

@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    
    # 获取当前用户
    user = User.query.filter_by(username=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # 获取服务历史
    service_history = ServiceRequest.query.filter_by(user_id=user.id).all()
    history_list = [
        {
            "service_id": sr.service_id,
            "target": sr.target_url,
            "timestamp": sr.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": sr.status,
            "cost": sr.cost
        }
        for sr in service_history
    ]
    
    return jsonify({
        "username": user.username,
        "email": user.email,
        "account_balance": user.account_balance,
        "service_history": history_list
    }), 200

# 运行应用
if __name__ == '__main__':
    app.run(debug=True, port=5000)
