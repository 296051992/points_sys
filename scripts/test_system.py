"""
系统验证测试脚本
运行此脚本验证所有核心功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("=" * 60)
    print("微信小程序积分兑换系统 - 验证测试")
    print("=" * 60)

    # 1. 测试导入
    print("\n[1/7] 测试模块导入...")
    from app.config import settings
    from app.db import SessionLocal, init_db
    from app.models import User, Product, PointsLedger, RedeemOrder
    from app.services.points import adjust_points, redeem_product, get_ledger
    from app.auth import create_access_token
    print("✓ 所有模块导入成功")

    # 2. 测试配置
    print("\n[2/7] 测试配置加载...")
    print(f"  - 数据库路径: {settings.DB_PATH}")
    print(f"  - 管理员用户: {settings.ADMIN_USERNAME}")
    print(f"  - 微信APPID: {settings.WECHAT_APPID[:8]}...")
    print("✓ 配置加载成功")

    # 3. 初始化数据库
    print("\n[3/7] 初始化数据库...")
    init_db()
    print("✓ 数据库表创建成功")

    # 4. 插入测试商品
    print("\n[4/7] 插入测试商品...")
    db = SessionLocal()
    try:
        # 检查是否已有商品
        existing = db.query(Product).count()
        if existing == 0:
            products = [
                Product(
                    name="星巴克咖啡券",
                    description="星巴克中杯咖啡兑换券一张",
                    points_cost=500,
                    stock=100,
                    is_active=1
                ),
                Product(
                    name="精美笔记本",
                    description="A5 尺寸精装笔记本",
                    points_cost=300,
                    stock=50,
                    is_active=1
                ),
                Product(
                    name="10元话费充值",
                    description="话费直充",
                    points_cost=100,
                    stock=-1,
                    is_active=1
                )
            ]
            for p in products:
                db.add(p)
            db.commit()
            print(f"✓ 成功插入 {len(products)} 个商品")
        else:
            print(f"✓ 数据库中已有 {existing} 个商品")
    finally:
        db.close()

    # 5. 测试管理员JWT
    print("\n[5/7] 测试JWT认证...")
    admin_token = create_access_token({"sub": "admin", "type": "admin"})
    user_token = create_access_token({"sub": "test_openid", "type": "user"})
    print(f"  - 管理员token: {admin_token[:20]}...")
    print(f"  - 用户token: {user_token[:20]}...")
    print("✓ JWT生成成功")

    # 6. 测试积分业务
    print("\n[6/7] 测试积分业务...")
    db = SessionLocal()
    try:
        test_openid = "test_user_123"

        # 加积分
        ledger = adjust_points(db, test_openid, 1000, "测试加分", "admin")
        print(f"  - 加分成功: +1000分，余额: {ledger.balance_after}")

        # 查询用户
        user = db.query(User).filter(User.openid == test_openid).first()
        print(f"  - 用户余额: {user.points_balance}")

        # 查询流水
        ledgers, total = get_ledger(db, test_openid, 1, 10)
        print(f"  - 流水记录: {total} 条")

        print("✓ 积分业务测试通过")
    finally:
        db.close()

    # 7. 测试兑换流程
    print("\n[7/7] 测试兑换流程...")
    db = SessionLocal()
    try:
        # 获取第一个商品
        product = db.query(Product).first()
        if product:
            print(f"  - 测试商品: {product.name} ({product.points_cost}分)")

            # 确保用户有足够积分
            user = db.query(User).filter(User.openid == test_openid).first()
            if user.points_balance < product.points_cost:
                adjust_points(db, test_openid, 1000, "补充积分", "admin")

            # 执行兑换
            order = redeem_product(db, test_openid, product.id)
            print(f"  - 订单号: {order.order_no}")
            print(f"  - 订单状态: {order.status}")

            # 验证余额
            user = db.query(User).filter(User.openid == test_openid).first()
            print(f"  - 兑换后余额: {user.points_balance}")

            print("✓ 兑换流程测试通过")
        else:
            print("! 没有可用商品进行测试")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！系统运行正常！")
    print("=" * 60)

    print("\n下一步操作:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 启动服务: uvicorn app.main:app --reload")
    print("3. 访问文档: http://localhost:8000/docs")
    print("4. 管理员账号: admin / admin123")

except ImportError as e:
    print(f"\n✗ 导入错误: {e}")
    print("\n请先安装依赖:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
