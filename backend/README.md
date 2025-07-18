# Backend Architecture

## 目录结构

```
backend/
├── __init__.py              # 模块初始化
├── app.py                   # 主应用类和工厂函数
├── config.py                # 配置管理
├── proxy_server.py          # 代理服务器核心实现
├── api_routes.py            # API路由处理
├── websocket_handler.py     # WebSocket事件处理
└── utils.py                 # 工具函数
```

## 模块功能

### 1. proxy_server.py - 代理服务器核心
- **ProxyServer类**: 实现HTTP和SOCKS5代理协议
- **实时流量监控**: 在`forward_data`方法中实时统计流量
- **连接管理**: 管理所有活跃连接，提供连接统计
- **协议支持**: 
  - HTTP代理: 支持GET、POST、CONNECT等方法
  - SOCKS5代理: 完整实现SOCKS5协议规范

### 2. api_routes.py - API路由
- **ProxyAPI类**: 封装所有代理相关的API端点
- **路由管理**: 
  - `/api/proxy/status` - 获取代理状态
  - `/api/proxy/start` - 启动代理服务
  - `/api/proxy/stop` - 停止代理服务
  - `/api/proxy/test` - 测试代理连接
  - `/api/connections` - 获取连接信息
- **健康检查**: `/health`和`/ready`端点

### 3. websocket_handler.py - 实时通信
- **SocketIOHandler类**: 处理WebSocket事件
- **实时监控**: 定期广播代理状态和流量数据
- **事件处理**: 连接、断开、状态请求等事件
- **数据推送**: 实时推送流量统计到前端

### 4. config.py - 配置管理
- **Config类**: 基础配置类
- **环境配置**: 开发、生产、测试环境配置
- **灵活配置**: 支持环境变量覆盖默认配置

### 5. app.py - 主应用
- **ProxyApp类**: 应用主类，整合所有组件
- **应用工厂**: `create_app`函数，支持不同环境配置
- **监控线程**: 自动启动状态监控和数据广播

### 6. utils.py - 工具函数
- **格式化函数**: 字节数、时间间隔格式化
- **网络工具**: URL验证、端口检查、IP获取
- **安全工具**: 速率限制器、连接池管理
- **日志工具**: 连接事件记录

## 流量代理功能分析

### ✅ 已实现的核心功能

#### 1. 多协议代理支持
- **HTTP代理**: 处理HTTP/HTTPS请求，支持CONNECT方法
- **SOCKS5代理**: 完整实现SOCKS5协议，支持域名和IP连接

#### 2. 实时流量捕获 🔥
- **字节级统计**: 在`forward_data`方法中实时记录每个连接的上传下载字节数
- **全局流量**: 累计所有连接的总流量
- **连接级监控**: 每个连接独立统计开始时间、目标地址、流量数据

#### 3. WebSocket实时推送 📡
- **状态广播**: 每2秒通过WebSocket推送最新状态
- **连接更新**: 实时推送新连接、断开连接事件
- **流量图表**: 前端基于实时数据绘制流量趋势图

#### 4. 连接管理
- **并发连接**: 支持多个客户端同时连接
- **连接追踪**: 记录每个连接的详细信息
- **资源清理**: 连接结束后自动清理资源

### 📊 流量监控机制

```python
def forward_data(self, client_sock, remote, connection_id):
    """实时流量监控的核心实现"""
    while self.running:
        # 使用select监控socket状态
        r, _, _ = select.select([client_sock, remote], [], [], 1.0)
        for s in r:
            data = s.recv(4096)
            if s is client_sock:
                # 客户端到服务器 - 上传流量
                remote.sendall(data)
                self.connections[connection_id]['bytes_sent'] += len(data)
            else:
                # 服务器到客户端 - 下载流量
                client_sock.sendall(data)
                self.connections[connection_id]['bytes_received'] += len(data)
```

### 🎯 前端实时展示

- **实时图表**: ECharts显示流量趋势
- **连接列表**: 显示所有活跃连接
- **统计面板**: 总连接数、总流量、运行时间
- **状态指示**: 代理运行状态实时更新

## 使用方法

### 1. 启动新的模块化后端
```bash
python app_new.py
```

### 2. API使用示例
```python
# 启动代理
POST /api/proxy/start
{
    "port": 8888,
    "proxy_type": "socks5"
}

# 获取实时状态
GET /api/proxy/status

# 测试连接
POST /api/proxy/test
{
    "url": "http://httpbin.org/ip"
}
```

### 3. WebSocket连接
```javascript
const socket = io('http://localhost:5000');
socket.on('proxy_stats', (data) => {
    console.log('实时状态:', data);
});
```

## 技术优势

1. **模块化设计**: 每个功能独立模块，便于维护和扩展
2. **实时监控**: WebSocket + 定时广播，确保数据实时性
3. **协议完整**: 同时支持HTTP和SOCKS5代理
4. **流量精确**: 字节级流量统计，精确监控
5. **配置灵活**: 支持多环境配置，生产就绪
6. **错误处理**: 完善的异常处理和日志记录

## 性能特点

- **并发处理**: 多线程处理多个连接
- **内存效率**: 及时清理断开的连接
- **网络优化**: 使用select实现高效数据转发
- **实时性**: 2秒广播间隔，保证界面流畅更新
