from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models import User, PointsLedger, Product, RedeemOrder, PointsLedgerType, OrderStatus
import uuid


class InsufficientPointsError(Exception):
    """积分不足错误"""
    pass


class OutOfStockError(Exception):
    """库存不足错误"""
    pass


class ProductNotFoundError(Exception):
    """商品不存在错误"""
    pass


class ProductNotActiveError(Exception):
    """商品未上架错误"""
    pass


def adjust_points(
    db: Session,
    openid: str,
    delta: int,
    reason: str,
    operator: str,
    ref_id: str = None
) -> PointsLedger:
    """
    管理员调整用户积分

    Args:
        db: 数据库会话
        openid: 用户openid
        delta: 积分变化量（正数加分，负数扣分）
        reason: 变化原因
        operator: 操作人
        ref_id: 关联单号

    Returns:
        积分流水记录

    Raises:
        InsufficientPointsError: 积分不足
    """
    # 获取或创建用户
    user = db.query(User).filter(User.openid == openid).with_for_update().first()
    if not user:
        user = User(openid=openid, points_balance=0)
        db.add(user)
        db.flush()  # 获取用户ID

    # 检查扣分后余额是否为负
    new_balance = user.points_balance + delta
    if new_balance < 0:
        raise InsufficientPointsError(f"积分不足，当前余额: {user.points_balance}，需要: {abs(delta)}")

    # 更新用户余额
    user.points_balance = new_balance

    # 记录流水
    ledger_type = PointsLedgerType.MANUAL_ADD if delta > 0 else PointsLedgerType.MANUAL_SUB
    ledger = PointsLedger(
        openid=openid,
        delta=delta,
        balance_after=new_balance,
        type=ledger_type,
        reason=reason,
        operator=operator,
        ref_id=ref_id
    )
    db.add(ledger)
    db.commit()
    db.refresh(ledger)

    return ledger


def redeem_product(
    db: Session,
    openid: str,
    product_id: int
) -> RedeemOrder:
    """
    用户兑换商品

    Args:
        db: 数据库会话
        openid: 用户openid
        product_id: 商品ID

    Returns:
        兑换订单

    Raises:
        ProductNotFoundError: 商品不存在
        ProductNotActiveError: 商品未上架
        InsufficientPointsError: 积分不足
        OutOfStockError: 库存不足
    """
    # 开启事务
    # 锁定用户行
    user = db.query(User).filter(User.openid == openid).with_for_update().first()
    if not user:
        user = User(openid=openid, points_balance=0)
        db.add(user)
        db.flush()

    # 锁定商品行
    product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
    if not product:
        raise ProductNotFoundError("商品不存在")

    if not product.is_active:
        raise ProductNotActiveError("商品已下架")

    # 检查积分
    if user.points_balance < product.points_cost:
        raise InsufficientPointsError(
            f"积分不足，当前余额: {user.points_balance}，需要: {product.points_cost}"
        )

    # 检查库存（-1表示无限库存）
    if product.stock != -1 and product.stock <= 0:
        raise OutOfStockError("商品库存不足")

    # 扣库存
    if product.stock != -1:
        product.stock -= 1

    # 扣积分
    user.points_balance -= product.points_cost

    # 生成订单号
    order_no = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"

    # 记录积分流水
    ledger = PointsLedger(
        openid=openid,
        delta=-product.points_cost,
        balance_after=user.points_balance,
        type=PointsLedgerType.REDEEM,
        reason=f"兑换商品：{product.name}",
        operator="SYSTEM",
        ref_id=order_no
    )
    db.add(ledger)

    # 生成订单
    order = RedeemOrder(
        order_no=order_no,
        openid=openid,
        product_id=product.id,
        product_name=product.name,
        points_cost=product.points_cost,
        status=OrderStatus.PENDING
    )
    db.add(order)

    db.commit()
    db.refresh(order)

    return order


def get_ledger(
    db: Session,
    openid: str,
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[PointsLedger], int]:
    """
    查询用户积分流水

    Args:
        db: 数据库会话
        openid: 用户openid
        page: 页码（从1开始）
        page_size: 每页数量

    Returns:
        (流水列表, 总数)
    """
    query = db.query(PointsLedger).filter(PointsLedger.openid == openid)
    total = query.count()

    ledgers = query.order_by(desc(PointsLedger.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return ledgers, total


def cancel_order_with_refund(
    db: Session,
    order_no: str,
    operator: str
) -> RedeemOrder:
    """
    取消订单并退款

    Args:
        db: 数据库会话
        order_no: 订单号
        operator: 操作人

    Returns:
        订单对象
    """
    # 锁定订单
    order = db.query(RedeemOrder).filter(RedeemOrder.order_no == order_no).with_for_update().first()
    if not order:
        raise ValueError("订单不存在")

    if order.status != OrderStatus.PENDING:
        raise ValueError("只能取消待发货订单")

    # 锁定用户
    user = db.query(User).filter(User.openid == order.openid).with_for_update().first()

    # 退还积分
    user.points_balance += order.points_cost

    # 记录流水
    ledger = PointsLedger(
        openid=order.openid,
        delta=order.points_cost,
        balance_after=user.points_balance,
        type=PointsLedgerType.REFUND,
        reason=f"取消订单退款：{order.product_name}",
        operator=operator,
        ref_id=order_no
    )
    db.add(ledger)

    # 恢复库存
    product = db.query(Product).filter(Product.id == order.product_id).with_for_update().first()
    if product and product.stock != -1:
        product.stock += 1

    # 更新订单状态
    order.status = OrderStatus.CANCELLED

    db.commit()
    db.refresh(order)

    return order
