"""
代理服务器核心模块
实现HTTP和SOCKS5代理服务器功能
支持管理网站绕过，避免代理悖论
"""

import socket
import threading
import select
import ssl
import logging
import os
import random
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyServer:
    """
    代理服务器类，支持HTTP和SOCKS5协议
    包含管理网站绕过逻辑，防止代理悖论
    """
    
    def __init__(self, host='0.0.0.0', port=8888, proxy_type='http'):
        """
        初始化代理服务器
        
        Args:
            host (str): 监听地址
            port (int): 监听端口
            proxy_type (str): 代理类型 ('http' 或 'socks5')
        """
        self.host = host
        self.port = port
        self.actual_port = port  # 实际使用的端口（可能与设定端口不同）
        self.proxy_type = proxy_type  # 'http' 或 'socks5'
        self.server_socket = None
        self.running = False
        self.connections = {}
        
        # 在Kubernetes环境中支持动态端口分配
        self.k8s_mode = os.getenv('KUBERNETES_SERVICE_HOST') is not None
        self.pod_name = os.getenv('HOSTNAME', 'unknown-pod')
        
        # 管理网站绕过列表 - 防止代理悖论
        self.bypass_hosts = self._get_bypass_hosts()
        
    def _get_bypass_hosts(self):
        """获取需要绕过代理的主机列表"""
        bypass_hosts = set()
        
        # 添加本地回环地址
        bypass_hosts.update(['localhost', '127.0.0.1', '::1'])
        
        # 添加管理API端口（通常是5000）
        bypass_hosts.update(['127.0.0.1:5000', 'localhost:5000'])
        
        # 在Kubernetes环境中，添加Service名称
        if self.k8s_mode:
            bypass_hosts.update([
                'backend-service', 'backend-service:5000',
                'frontend-service', 'frontend-service:80',
                'backend-service.vpn-proxy.svc.cluster.local',
                'frontend-service.vpn-proxy.svc.cluster.local'
            ])
            
        # 从环境变量获取额外的绕过主机
        bypass_env = os.getenv('PROXY_BYPASS_HOSTS', '')
        if bypass_env:
            bypass_hosts.update(host.strip() for host in bypass_env.split(','))
            
        logger.info(f"代理绕过主机列表: {bypass_hosts}")
        return bypass_hosts
    
    def _should_bypass_proxy(self, host, port=None):
        """检查是否应该绕过代理"""
        if not host:
            return False
            
        # 检查纯主机名
        if host in self.bypass_hosts:
            return True
            
        # 检查主机名:端口组合
        if port and f"{host}:{port}" in self.bypass_hosts:
            return True
            
        # 检查是否是管理API端口
        if port == 5000:
            logger.info(f"绕过管理API端口: {host}:{port}")
            return True
            
        # 检查是否是前端端口
        if port == 80 or port == 3000:
            logger.info(f"绕过前端端口: {host}:{port}")
            return True
            
        return False
        
    def find_available_port(self, start_port=8888, max_attempts=10):
        """
        寻找可用的端口
        
        Args:
            start_port (int): 起始端口
            max_attempts (int): 最大尝试次数
            
        Returns:
            int: 可用端口号，如果找不到则返回None
        """
        for i in range(max_attempts):
            try_port = start_port + i
            try:
                # 测试端口是否可用
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((self.host, try_port))
                test_socket.close()
                logger.info(f"Found available port: {try_port}")
                return try_port
            except OSError:
                logger.debug(f"Port {try_port} is not available")
                continue
        
        # 如果前面的端口都不可用，在高端口随机尝试
        for _ in range(5):
            random_port = random.randint(9000, 9999)
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((self.host, random_port))
                test_socket.close()
                logger.info(f"Found random available port: {random_port}")
                return random_port
            except OSError:
                continue
                
        return None
        
    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 在Kubernetes环境中尝试动态端口分配
            if self.k8s_mode:
                available_port = self.find_available_port(self.port)
                if available_port is None:
                    raise Exception("无法找到可用端口")
                self.actual_port = available_port
                logger.info(f"Kubernetes模式: Pod {self.pod_name} 使用端口 {self.actual_port}")
            else:
                self.actual_port = self.port
            
            self.server_socket.bind((self.host, self.actual_port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"{self.proxy_type.upper()} proxy server started on {self.host}:{self.actual_port}")
            
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
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connections: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}")
            raise
    
    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info(f"{self.proxy_type.upper()} proxy server stopped")
        
    def handle_client(self, client_sock, addr, connection_id):
        """
        处理客户端连接
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
        try:
            if self.proxy_type == 'http':
                self.handle_http_proxy(client_sock, addr, connection_id)
            else:
                self.handle_socks5_proxy(client_sock, addr, connection_id)
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            client_sock.close()
            
            # 清理连接记录
            if connection_id in self.connections:
                del self.connections[connection_id]
    
    def handle_http_proxy(self, client_sock, addr, connection_id):
        """
        处理HTTP代理请求
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
        remote = None
        try:
            # 读取HTTP请求
            request = b''
            while b'\r\n\r\n' not in request:
                chunk = client_sock.recv(4096)
                if not chunk:
                    return
                request += chunk
            
            # 解析HTTP请求
            request_line = request.split(b'\r\n')[0].decode('utf-8')
            method, url, version = request_line.split(' ')
            
            if method == 'CONNECT':
                # HTTPS连接 (CONNECT方法)
                host, port = url.split(':')
                port = int(port)
                
                # 检查是否需要绕过代理
                if self._should_bypass_proxy(host, port):
                    logger.info(f"绕过代理访问: {host}:{port}")
                    client_sock.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
                    # 直接关闭连接，让客户端重新直连
                    return
                
                # 连接目标服务器
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.settimeout(10)
                remote.connect((host, port))
                
                # 更新连接信息
                self.connections[connection_id]['target'] = f"{host}:{port}"
                
                # 回复连接建立成功
                client_sock.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
                
                # 开始数据转发
                self.forward_data(client_sock, remote, connection_id)
                
            else:
                # HTTP请求 (GET, POST等)
                if url.startswith('http://'):
                    # 解析URL
                    parsed = urlparse(url)
                    host = parsed.hostname
                    port = parsed.port or 80
                    path = parsed.path or '/'
                    if parsed.query:
                        path += '?' + parsed.query
                        
                    # 检查是否需要绕过代理
                    if self._should_bypass_proxy(host, port):
                        logger.info(f"绕过代理HTTP请求: {host}:{port}")
                        client_sock.sendall(b'HTTP/1.1 502 Bypassed\r\n\r\n')
                        return
                else:
                    # 相对URL，从Host头获取
                    host_header = None
                    for line in request.split(b'\r\n')[1:]:
                        if line.startswith(b'Host: '):
                            host_header = line[6:].decode('utf-8')
                            break
                    
                    if host_header:
                        if ':' in host_header:
                            host, port_str = host_header.split(':')
                            port = int(port_str)
                        else:
                            host = host_header
                            port = 80
                        path = url
                        
                        # 检查是否需要绕过代理
                        if self._should_bypass_proxy(host, port):
                            logger.info(f"绕过代理相对HTTP请求: {host}:{port}")
                            client_sock.sendall(b'HTTP/1.1 502 Bypassed\r\n\r\n')
                            return
                    else:
                        client_sock.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')
                        return
                
                # 连接目标服务器
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.settimeout(10)
                remote.connect((host, port))
                
                # 更新连接信息
                self.connections[connection_id]['target'] = f"{host}:{port}"
                
                # 修改请求为相对路径并转发
                modified_request = request.replace(url.encode(), path.encode())
                remote.sendall(modified_request)
                
                # 开始数据转发
                self.forward_data(client_sock, remote, connection_id)
                
        except Exception as e:
            logger.error(f"HTTP proxy error: {e}")
            try:
                client_sock.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            except:
                pass
        finally:
            if remote:
                remote.close()
    
    def handle_socks5_proxy(self, client_sock, addr, connection_id):
        """
        处理SOCKS5代理请求
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
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
                
            # 检查是否需要绕过代理
            if self._should_bypass_proxy(target_addr, port):
                logger.info(f"绕过代理SOCKS5请求: {target_addr}:{port}")
                # 返回连接拒绝
                reply = b'\x05\x02\x00\x01' + socket.inet_aton('0.0.0.0') + (0).to_bytes(2, 'big')
                client_sock.sendall(reply)
                return
                
            # 连接目标服务器
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(10)
            remote.connect((target_addr, port))
            
            # 更新连接信息
            self.connections[connection_id]['target'] = f"{target_addr}:{port}"
            
            # 回复成功，使用实际端口号
            reply = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + (self.actual_port).to_bytes(2, 'big')
            client_sock.sendall(reply)
            
            # 开始数据转发
            self.forward_data(client_sock, remote, connection_id)
            
        except Exception as e:
            logger.error(f"SOCKS5 proxy error: {e}")
        finally:
            if remote:
                remote.close()
    
    def forward_data(self, client_sock, remote, connection_id):
        """
        数据转发函数 - 实现实时流量监控
        
        Args:
            client_sock: 客户端socket
            remote: 远程服务器socket  
            connection_id: 连接ID
        """
        sockets = [client_sock, remote]
        while self.running:
            try:
                r, _, _ = select.select(sockets, [], [], 1.0)
                for s in r:
                    data = s.recv(4096)
                    if not data:
                        return
                        
                    if s is client_sock:
                        # 客户端到服务器的数据
                        remote.sendall(data)
                        self.connections[connection_id]['bytes_sent'] += len(data)
                    else:
                        # 服务器到客户端的数据
                        client_sock.sendall(data)
                        self.connections[connection_id]['bytes_received'] += len(data)
                        
            except Exception as e:
                logger.error(f"Error in data forwarding: {e}")
                break
    
    def get_connections_stats(self):
        """获取连接统计信息"""
        total_bytes = 0
        active_connections = []
        
        for conn_id, info in self.connections.items():
            total_bytes += info['bytes_sent'] + info['bytes_received']
            active_connections.append({
                'id': conn_id,
                'target': info['target'],
                'bytes_sent': info['bytes_sent'],
                'bytes_received': info['bytes_received'],
                'start_time': info['start_time'].isoformat()
            })
        
        return {
            'total_connections': len(self.connections),
            'total_bytes': total_bytes,
            'active_connections': active_connections,
            'actual_port': self.actual_port,  # 添加实际端口信息
            'k8s_mode': self.k8s_mode,
            'pod_name': self.pod_name,
            'bypass_hosts': list(self.bypass_hosts)
        }
    
    def get_actual_port(self):
        """获取实际使用的端口号"""
        return self.actual_port
