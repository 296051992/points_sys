"""
快速生成测试数据
用于演示和测试
"""
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User, Product
from app.services.points import adjust_points, redeem_product


def generate_test_users(count=10):
    """生成测试用户"""
    db = SessionLocal()
    try:
        print(f"正在生成 {count} 个测试用户...")

        nicknames = [
            "张三", "李四", "王五", "赵六", "孙七",
            "小明", "小红", "小华", "小刚", "小丽",
            "阿强", "阿美", "阿花", "阿龙", "阿凤"
        ]

        created_count = 0
        for i in range(count):
            openid = f"test_user_{i+1:03d}"

            # 检查是否已存在
            existing = db.query(User).filter(User.openid == openid).first()
            if existing:
                print(f"  跳过已存在用户: {openid}")
                continue

            # 创建用户并随机加积分
            points = random.randint(100, 2000)
            nickname = random.choice(nicknames) + str(random.randint(1, 999))

            adjust_points(
                db=db,
                openid=openid,
                delta=points,
                reason="初始积分",
                operator="SYSTEM"
            )

            # 更新昵称
            user = db.query(User).filter(User.openid == openid).first()
            user.nickname = nickname
            db.commit()

            created_count += 1
            print(f"  创建用户: {openid} ({nickname}) - {points}积分")

        print(f"\n成功创建 {created_count} 个测试用户")

    finally:
        db.close()


def generate_test_products(count=5):
    """生成测试商品"""
    db = SessionLocal()
    try:
        print(f"\n正在生成 {count} 个测试商品...")

        product_templates = [
            ("优酷VIP月卡", "优酷视频VIP会员1个月", 500, 20),
            ("爱奇艺VIP月卡", "爱奇艺VIP会员1个月", 500, 20),
            ("腾讯视频VIP月卡", "腾讯视频VIP会员1个月", 500, 20),
            ("50元话费充值", "中国移动/联通/电信话费充值", 500, -1),
            ("20元话费充值", "中国移动/联通/电信话费充值", 200, -1),
            ("小米无线鼠标", "小米便携式无线鼠标", 800, 10),
            ("罗技键盘", "罗技K380蓝牙键盘", 1200, 5),
            ("星巴克大杯咖啡券", "星巴克大杯任意咖啡兑换券", 600, 50),
            ("KFC优惠券", "肯德基30元代金券", 300, 100),
            ("电影票兑换券", "万达/CGV电影票", 800, 30),
        ]

        existing_count = db.query(Product).count()

        created_count = 0
        for i in range(min(count, len(product_templates))):
            if existing_count + created_count >= count + 3:  # 假设已有3个初始商品
                break

            name, desc, points, stock = product_templates[i]

            product = Product(
                name=name,
                description=desc,
                points_cost=points,
                stock=stock,
                is_active=1
            )
            db.add(product)
            created_count += 1

            stock_str = "无限" if stock == -1 else str(stock)
            print(f"  创建商品: {name} - {points}积分 (库存: {stock_str})")

        db.commit()
        print(f"\n成功创建 {created_count} 个测试商品")

    finally:
        db.close()


def generate_test_orders(count=10):
    """生成测试订单"""
    db = SessionLocal()
    try:
        print(f"\n正在生成 {count} 个测试订单...")

        # 获取所有用户和商品
        users = db.query(User).all()
        products = db.query(Product).filter(Product.is_active == 1).all()

        if not users:
            print("  错误: 没有用户，请先生成测试用户")
            return

        if not products:
            print("  错误: 没有商品，请先生成测试商品")
            return

        created_count = 0
        for i in range(count):
            # 随机选择用户和商品
            user = random.choice(users)
            product = random.choice(products)

            # 确保用户有足够积分
            if user.points_balance < product.points_cost:
                adjust_points(
                    db=db,
                    openid=user.openid,
                    delta=product.points_cost * 2,
                    reason="补充积分用于测试兑换",
                    operator="SYSTEM"
                )
                db.commit()
                # 刷新用户对象
                db.refresh(user)

            # 执行兑换
            try:
                order = redeem_product(db, user.openid, product.id)
                created_count += 1
                print(f"  订单 {created_count}: {user.nickname or user.openid} 兑换 {product.name}")
            except Exception as e:
                print(f"  跳过: {e}")

        print(f"\n成功创建 {created_count} 个测试订单")

    finally:
        db.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成测试数据")
    parser.add_argument("--users", type=int, default=0, help="生成测试用户数量")
    parser.add_argument("--products", type=int, default=0, help="生成测试商品数量")
    parser.add_argument("--orders", type=int, default=0, help="生成测试订单数量")
    parser.add_argument("--all", action="store_true", help="生成所有类型的测试数据")

    args = parser.parse_args()

    try:
        if args.all:
            generate_test_users(10)
            generate_test_products(5)
            generate_test_orders(15)
        else:
            if args.users > 0:
                generate_test_users(args.users)
            if args.products > 0:
                generate_test_products(args.products)
            if args.orders > 0:
                generate_test_orders(args.orders)

            if not any([args.users, args.products, args.orders]):
                print("请使用 --help 查看使用说明")
                print("\n示例:")
                print("  python scripts/generate_test_data.py --all")
                print("  python scripts/generate_test_data.py --users 10")
                print("  python scripts/generate_test_data.py --products 5")
                print("  python scripts/generate_test_data.py --orders 20")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
