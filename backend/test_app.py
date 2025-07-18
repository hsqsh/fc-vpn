#!/usr/bin/env python3
"""
完整的应用启动测试
"""

print("🚀 开始VPN代理应用测试")
print("=" * 50)

def test_basic_imports():
    """测试基础模块导入"""
    print("1. 测试基础模块导入...")
    try:
        from flask import Flask
        print("   ✅ Flask导入成功")
        
        from flask_cors import CORS
        print("   ✅ Flask-CORS导入成功")
        
        from flask_socketio import SocketIO
        print("   ✅ Flask-SocketIO导入成功")
        
        from config import get_config
        print("   ✅ config导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 基础模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_custom_modules():
    """测试自定义模块导入"""
    print("\n2. 测试自定义模块导入...")
    try:
        from websocket_handler import SocketIOHandler
        print("   ✅ websocket_handler导入成功")
        
        from api_routes import ProxyAPI
        print("   ✅ api_routes导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 自定义模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n3. 测试应用创建...")
    try:
        from app import ProxyApp, create_app
        print("   ✅ app模块导入成功")
        
        # 测试开发环境应用创建
        dev_app = create_app('development')
        print("   ✅ 开发环境应用创建成功")
        
        # 测试生产环境应用创建
        prod_app = create_app('production')
        print("   ✅ 生产环境应用创建成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """测试路由注册"""
    print("\n4. 测试路由注册...")
    try:
        from app import create_app
        
        app_instance = create_app('development')
        flask_app = app_instance.get_app()
        
        # 获取所有路由
        routes = [str(rule) for rule in flask_app.url_map.iter_rules()]
        print(f"   ✅ 总共注册了 {len(routes)} 个路由")
        
        # 检查关键路由
        key_routes = ['/health', '/ready', '/metrics', '/api/proxy/status']
        for route in key_routes:
            if any(route in r for r in routes):
                print(f"   ✅ 关键路由 {route} 已注册")
            else:
                print(f"   ⚠️  关键路由 {route} 未找到")
        
        return True
    except Exception as e:
        print(f"   ❌ 路由测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    try:
        # 基础导入测试
        if not test_basic_imports():
            print("\n❌ 基础模块测试失败")
            return False
        
        # 自定义模块测试
        if not test_custom_modules():
            print("\n❌ 自定义模块测试失败")
            return False
        
        # 应用创建测试
        if not test_app_creation():
            print("\n❌ 应用创建测试失败")
            return False
        
        # 路由测试
        if not test_routes():
            print("\n❌ 路由测试失败")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！应用可以正常启动")
        print("\n建议下一步测试:")
        print("  - 运行: python app.py (启动开发服务器)")
        print("  - 访问: http://localhost:5000/health (健康检查)")
        print("  - 访问: http://localhost:5000/ready (就绪检查)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    main()
