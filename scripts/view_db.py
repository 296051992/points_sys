"""
数据库查看工具
可以方便地查看数据库中的数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User, Product, PointsLedger, RedeemOrder
from sqlalchemy import func


def print_table_header(title):
    """打印表头"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def view_users():
    """查看用户列表"""
    db = SessionLocal()
    try:
        print_table_header("用户列表")
        users = db.query(User).all()

        if not users:
            print("  暂无用户数据")
            return

        print(f"{'ID':<5} {'OpenID':<25} {'昵称':<15} {'积分余额':<10} {'创建时间':<20}")
        print("-" * 80)

        for user in users:
            print(f"{user.id:<5} {user.openid:<25} {(user.nickname or 'N/A'):<15} {user.points_balance:<10} {str(user.created_at)[:19]:<20}")

        print(f"\n总计: {len(users)} 个用户")
    finally:
        db.close()


def view_products():
    """查看商品列表"""
    db = SessionLocal()
    try:
        print_table_header("商品列表")
        products = db.query(Product).all()

        if not products:
            print("  暂无商品数据")
            return

        print(f"{'ID':<5} {'商品名称':<20} {'积分':<8} {'库存':<8} {'状态':<6} {'创建时间':<20}")
        print("-" * 80)

        for product in products:
            stock_str = "无限" if product.stock == -1 else str(product.stock)
            status_str = "上架" if product.is_active else "下架"
            print(f"{product.id:<5} {product.name:<20} {product.points_cost:<8} {stock_str:<8} {status_str:<6} {str(product.created_at)[:19]:<20}")

        print(f"\n总计: {len(products)} 个商品")
    finally:
        db.close()


def view_orders():
    """查看订单列表"""
    db = SessionLocal()
    try:
        print_table_header("订单列表")
        orders = db.query(RedeemOrder).order_by(RedeemOrder.created_at.desc()).limit(20).all()

        if not orders:
            print("  暂无订单数据")
            return

        print(f"{'ID':<5} {'订单号':<25} {'商品名称':<20} {'积分':<8} {'状态':<10} {'创建时间':<20}")
        print("-" * 80)

        for order in orders:
            status_map = {
                "PENDING": "待发货",
                "FULFILLED": "已发货",
                "CANCELLED": "已取消"
            }
            status_str = status_map.get(order.status.value, order.status.value)
            print(f"{order.id:<5} {order.order_no:<25} {order.product_name:<20} {order.points_cost:<8} {status_str:<10} {str(order.created_at)[:19]:<20}")

        print(f"\n显示最近 {len(orders)} 个订单")
    finally:
        db.close()


def view_ledger(openid=None, limit=20):
    """查看积分流水"""
    db = SessionLocal()
    try:
        print_table_header(f"积分流水 {f'(用户: {openid})' if openid else '(全部)'}")

        query = db.query(PointsLedger)
        if openid:
            query = query.filter(PointsLedger.openid == openid)

        ledgers = query.order_by(PointsLedger.created_at.desc()).limit(limit).all()

        if not ledgers:
            print("  暂无流水数据")
            return

        print(f"{'ID':<5} {'OpenID':<20} {'变动':<8} {'余额':<8} {'类型':<15} {'原因':<25} {'时间':<20}")
        print("-" * 110)

        for ledger in ledgers:
            delta_str = f"+{ledger.delta}" if ledger.delta > 0 else str(ledger.delta)
            type_map = {
                "MANUAL_ADD": "管理员加分",
                "MANUAL_SUB": "管理员扣分",
                "REDEEM": "兑换商品",
                "REFUND": "退款"
            }
            type_str = type_map.get(ledger.type.value, ledger.type.value)
            print(f"{ledger.id:<5} {ledger.openid:<20} {delta_str:<8} {ledger.balance_after:<8} {type_str:<15} {ledger.reason[:25]:<25} {str(ledger.created_at)[:19]:<20}")

        print(f"\n显示最近 {len(ledgers)} 条流水")
    finally:
        db.close()


def view_statistics():
    """查看统计信息"""
    db = SessionLocal()
    try:
        print_table_header("系统统计")

        # 用户统计
        user_count = db.query(User).count()
        total_points = db.query(func.sum(User.points_balance)).scalar() or 0

        # 商品统计
        product_count = db.query(Product).count()
        active_product_count = db.query(Product).filter(Product.is_active == 1).count()

        # 订单统计
        order_count = db.query(RedeemOrder).count()
        pending_count = db.query(RedeemOrder).filter(RedeemOrder.status == "PENDING").count()
        fulfilled_count = db.query(RedeemOrder).filter(RedeemOrder.status == "FULFILLED").count()
        cancelled_count = db.query(RedeemOrder).filter(RedeemOrder.status == "CANCELLED").count()

        # 积分流水统计
        ledger_count = db.query(PointsLedger).count()

        print(f"\n📊 用户统计:")
        print(f"  总用户数: {user_count}")
        print(f"  总积分数: {total_points}")
        print(f"  平均积分: {total_points / user_count if user_count > 0 else 0:.2f}")

        print(f"\n📦 商品统计:")
        print(f"  总商品数: {product_count}")
        print(f"  上架商品: {active_product_count}")
        print(f"  下架商品: {product_count - active_product_count}")

        print(f"\n🛒 订单统计:")
        print(f"  总订单数: {order_count}")
        print(f"  待发货: {pending_count}")
        print(f"  已发货: {fulfilled_count}")
        print(f"  已取消: {cancelled_count}")

        print(f"\n💰 流水统计:")
        print(f"  总流水数: {ledger_count}")

    finally:
        db.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库查看工具")
    parser.add_argument("--users", action="store_true", help="查看用户列表")
    parser.add_argument("--products", action="store_true", help="查看商品列表")
    parser.add_argument("--orders", action="store_true", help="查看订单列表")
    parser.add_argument("--ledger", type=str, nargs="?", const="", help="查看积分流水 (可选: 指定openid)")
    parser.add_argument("--stats", action="store_true", help="查看统计信息")
    parser.add_argument("--all", action="store_true", help="查看所有数据")

    args = parser.parse_args()

    # 如果没有任何参数，显示统计信息
    if not any([args.users, args.products, args.orders, args.ledger is not None, args.stats, args.all]):
        args.stats = True

    try:
        if args.all:
            view_statistics()
            view_users()
            view_products()
            view_orders()
            view_ledger(limit=20)
        else:
            if args.stats:
                view_statistics()
            if args.users:
                view_users()
            if args.products:
                view_products()
            if args.orders:
                view_orders()
            if args.ledger is not None:
                openid = args.ledger if args.ledger else None
                view_ledger(openid=openid, limit=20)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
