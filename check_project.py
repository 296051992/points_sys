"""
简单验证脚本 - 检查项目文件完整性
不需要安装任何依赖即可运行
"""
import os
import sys

def check_file(path, description):
    """检查文件是否存在"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✓ {description}: {path} ({size} bytes)")
        return True
    else:
        print(f"  ✗ {description}: {path} - 文件不存在")
        return False

def main():
    print("=" * 70)
    print("微信小程序积分兑换系统 - 项目完整性检查")
    print("=" * 70)

    checks = []

    # 核心应用文件
    print("\n[1/6] 检查核心应用文件...")
    checks.append(check_file("app/__init__.py", "应用初始化"))
    checks.append(check_file("app/main.py", "FastAPI入口"))
    checks.append(check_file("app/config.py", "配置管理"))
    checks.append(check_file("app/db.py", "数据库连接"))
    checks.append(check_file("app/models.py", "数据模型"))
    checks.append(check_file("app/schemas.py", "API数据结构"))
    checks.append(check_file("app/auth.py", "JWT认证"))

    print("\n[2/6] 检查服务层...")
    checks.append(check_file("app/services/__init__.py", "服务初始化"))
    checks.append(check_file("app/services/points.py", "积分服务"))
    checks.append(check_file("app/services/wechat.py", "微信服务"))

    print("\n[3/6] 检查路由层...")
    checks.append(check_file("app/routers/__init__.py", "路由初始化"))
    checks.append(check_file("app/routers/api.py", "小程序端接口"))
    checks.append(check_file("app/routers/admin.py", "管理端接口"))

    print("\n[4/6] 检查工具脚本...")
    checks.append(check_file("scripts/init_db.py", "数据库初始化"))
    checks.append(check_file("scripts/seed.py", "示例数据"))
    checks.append(check_file("scripts/test_system.py", "系统测试"))
    checks.append(check_file("scripts/test_api.py", "API测试"))
    checks.append(check_file("scripts/view_db.py", "数据库查看"))
    checks.append(check_file("scripts/generate_test_data.py", "测试数据生成"))
    checks.append(check_file("scripts/admin_cli.py", "管理CLI"))

    print("\n[5/6] 检查配置文件...")
    checks.append(check_file("requirements.txt", "依赖列表"))
    checks.append(check_file(".env.example", "配置模板"))
    checks.append(check_file(".env", "实际配置"))
    checks.append(check_file(".gitignore", "Git忽略"))
    checks.append(check_file("Dockerfile", "Docker配置"))
    checks.append(check_file("docker-compose.yml", "Docker Compose"))

    print("\n[6/6] 检查启动脚本和文档...")
    checks.append(check_file("start.bat", "Windows启动脚本"))
    checks.append(check_file("start.sh", "Linux启动脚本"))
    checks.append(check_file("README.md", "项目文档"))
    checks.append(check_file("API_TESTS.md", "API测试文档"))
    checks.append(check_file("QUICKSTART.md", "快速开始指南"))

    # 统计结果
    total = len(checks)
    passed = sum(checks)

    print("\n" + "=" * 70)
    print(f"检查结果: {passed}/{total} 文件存在")
    print("=" * 70)

    if passed == total:
        print("\n✓ 所有文件完整！项目结构正确。")
        print("\n下一步:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 初始化数据库: python scripts/init_db.py")
        print("3. 插入示例数据: python scripts/seed.py")
        print("4. 启动服务: uvicorn app.main:app --reload")
        print("5. 访问文档: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n✗ 有 {total - passed} 个文件缺失！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
