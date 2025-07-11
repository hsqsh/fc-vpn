# FC-VPN 门户网站

这是一个基于Vue和Flask的云原生VPN服务门户网站，用于演示如何构建支持Kubernetes的VPN服务管理系统。

## 项目结构

```
fc-vpn-portal/
├── backend/               # Flask后端
│   ├── app.py            # 主应用代码
│   └── requirements.txt  # Python依赖
└── frontend/             # Vue前端
    ├── package.json      # 项目配置
    ├── public/           # 静态文件
    └── src/              # 源代码
```

## 功能特性

1. 用户注册与登录
2. VPN服务请求（输入目标URL）
3. 用户资料和服务历史查看
4. 模拟与Kubernetes API的交互
5. 简单的计费功能（每次服务请求消费$0.1）

## 后端设置

1. 进入backend目录
```powershell
cd .\fc-vpn-portal\backend\
```

2. 激活虚拟环境
```powershell
cd .venv/Scripts
.\activate
```

3. 运行Flask应用
```powershell
python app.py
```

## 前端设置

1. 进入frontend目录
```powershell
cd .\fc-vpn-portal\frontend\
```

2. 安装依赖
```powershell
npm install
```

3. 启动开发服务器
```powershell
npm run serve
```

Vue应用将在 http://localhost:8080 上运行。

## API端点

- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- GET /api/user/profile - 获取用户资料
- POST /api/service/request - 发起VPN服务请求

## K8s模拟说明

本项目使用`MockK8sOperatorClient`类模拟与Kubernetes Operator的交互。在实际生产环境中，这部分应该替换为真实的Kubernetes API调用。
