#!/usr/bin/env python3
"""
生产环境启动脚本
专为Kubernetes容器环境设计
"""

import os
import logging
import sys
from pathlib import Path

# 设置Python路径
sys.path.insert(0, '/app')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/app.log') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主启动函数"""
    try:
        logger.info("🚀 启动VPN代理后端服务...")
        logger.info(f"Python版本: {sys.version}")
        logger.info(f"工作目录: {os.getcwd()}")
        
        # 检查环境变量
        flask_env = os.getenv('FLASK_ENV', 'production')
        port = int(os.getenv('PORT', '5000'))
        proxy_port = int(os.getenv('PROXY_PORT', '8888'))
        
        logger.info(f"环境: {flask_env}")
        logger.info(f"API端口: {port}")
        logger.info(f"代理端口: {proxy_port}")
        
        # 导入应用
        from app import create_app
        
        # 创建应用实例
        logger.info("创建应用实例...")
        app_instance = create_app(flask_env)
        
        # 启动应用
        logger.info("启动应用...")
        app_instance.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
