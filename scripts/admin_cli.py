"""
管理员CLI工具
提供命令行管理功能
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import User, Product, RedeemOrder, OrderStatus
from app.services.points import adjust_points, cancel_order_with_refund
import argparse


def add_points_command(args):
    """加积分命令"""
    db = SessionLocal()
    try:
        ledger = adjust_points(
            db=db,
            openid=args.openid,
            delta=args.points,
            reason=args.reason,
            operator="CLI"
        )
        print(f"✓ 成功为 {args.openid} 添加 {args.points} 积分")
        print(f"  当前余额: {ledger.balance_after}")
    except Exception as e:
        print(f"✗ 操作失败: {e}")
    finally:
        db.close()


def create_product_command(args):
    """创建商品命令"""
    db = SessionLocal()
    try:
        product = Product(
            name=args.name,
            description=args.description,
            points_cost=args.points,
            stock=args.stock,
            is_active=1
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        stock_str = "无限" if args.stock == -1 else str(args.stock)
        print(f"✓ 成功创建商品 ID={product.id}")
        print(f"  名称: {product.name}")
        print(f"  积分: {product.points_cost}")
        print(f"  库存: {stock_str}")
    except Exception as e:
        print(f"✗ 操作失败: {e}")
        db.rollback()
    finally:
        db.close()


def list_users_command(args):
    """列出用户命令"""
    db = SessionLocal()
    try:
        query = db.query(User)

        if args.min_points:
            query = query.filter(User.points_balance >= args.min_points)

        users = query.order_by(User.points_balance.desc()).limit(args.limit).all()

        print(f"\n{'OpenID':<25} {'昵称':<15} {'积分':<10}")
        print("-" * 50)

        for user in users:
            print(f"{user.openid:<25} {(user.nickname or 'N/A'):<15} {user.points_balance:<10}")

        print(f"\n共 {len(users)} 个用户")
    finally:
        db.close()


def fulfill_order_command(args):
    """完成订单命令"""
    db = SessionLocal()
    try:
        order = db.query(RedeemOrder).filter(RedeemOrder.order_no == args.order_no).first()

        if not order:
            print(f"✗ 订单不存在: {args.order_no}")
            return

        if order.status != OrderStatus.PENDING:
            print(f"✗ 订单状态错误: {order.status.value}")
            return

        order.status = OrderStatus.FULFILLED
        db.commit()

        print(f"✓ 订单 {args.order_no} 已标记为已发货")
        print(f"  用户: {order.openid}")
        print(f"  商品: {order.product_name}")
    except Exception as e:
        print(f"✗ 操作失败: {e}")
        db.rollback()
    finally:
        db.close()


def cancel_order_command(args):
    """取消订单命令"""
    db = SessionLocal()
    try:
        order = cancel_order_with_refund(db, args.order_no, "CLI")

        print(f"✓ 订单 {args.order_no} 已取消并退款")
        print(f"  用户: {order.openid}")
        print(f"  商品: {order.product_name}")
        print(f"  退还积分: {order.points_cost}")
    except Exception as e:
        print(f"✗ 操作失败: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="积分系统管理CLI工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 加积分命令
    add_parser = subparsers.add_parser("add-points", help="给用户加积分")
    add_parser.add_argument("openid", help="用户openid")
    add_parser.add_argument("points", type=int, help="积分数量")
    add_parser.add_argument("--reason", default="管理员充值", help="原因")
    add_parser.set_defaults(func=add_points_command)

    # 创建商品命令
    create_parser = subparsers.add_parser("create-product", help="创建商品")
    create_parser.add_argument("name", help="商品名称")
    create_parser.add_argument("points", type=int, help="所需积分")
    create_parser.add_argument("--description", default="", help="商品描述")
    create_parser.add_argument("--stock", type=int, default=-1, help="库存数量 (-1表示无限)")
    create_parser.set_defaults(func=create_product_command)

    # 列出用户命令
    list_parser = subparsers.add_parser("list-users", help="列出用户")
    list_parser.add_argument("--limit", type=int, default=20, help="显示数量")
    list_parser.add_argument("--min-points", type=int, help="最小积分筛选")
    list_parser.set_defaults(func=list_users_command)

    # 完成订单命令
    fulfill_parser = subparsers.add_parser("fulfill-order", help="完成订单")
    fulfill_parser.add_argument("order_no", help="订单号")
    fulfill_parser.set_defaults(func=fulfill_order_command)

    # 取消订单命令
    cancel_parser = subparsers.add_parser("cancel-order", help="取消订单并退款")
    cancel_parser.add_argument("order_no", help="订单号")
    cancel_parser.set_defaults(func=cancel_order_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
