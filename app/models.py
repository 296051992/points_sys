from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from datetime import datetime
from app.db import Base
import enum


class PointsLedgerType(str, enum.Enum):
    """积分流水类型"""
    MANUAL_ADD = "MANUAL_ADD"      # 管理员加分
    MANUAL_SUB = "MANUAL_SUB"      # 管理员扣分
    REDEEM = "REDEEM"              # 兑换商品
    REFUND = "REFUND"              # 退款


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "PENDING"            # 待发货
    FULFILLED = "FULFILLED"        # 已发货
    CANCELLED = "CANCELLED"        # 已取消


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, nullable=False, comment="微信openid")
    nickname = Column(String(100), nullable=True, comment="昵称")
    avatar_url = Column(String(500), nullable=True, comment="头像")
    points_balance = Column(Integer, default=0, nullable=False, comment="积分余额")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class PointsLedger(Base):
    """积分流水表"""
    __tablename__ = "points_ledger"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), index=True, nullable=False, comment="用户openid")
    delta = Column(Integer, nullable=False, comment="积分变化量（正数加分，负数扣分）")
    balance_after = Column(Integer, nullable=False, comment="变化后余额")
    type = Column(SQLEnum(PointsLedgerType), nullable=False, comment="流水类型")
    reason = Column(String(200), nullable=False, comment="变化原因")
    operator = Column(String(64), nullable=False, comment="操作人（SYSTEM/管理员用户名）")
    ref_id = Column(String(64), nullable=True, comment="关联单号（订单号等）")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="商品名称")
    description = Column(Text, nullable=True, comment="商品描述")
    image_url = Column(String(500), nullable=True, comment="商品图片")
    points_cost = Column(Integer, nullable=False, comment="所需积分")
    stock = Column(Integer, default=-1, nullable=False, comment="库存（-1表示无限）")
    is_active = Column(Integer, default=1, nullable=False, comment="是否上架（1上架，0下架）")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class RedeemOrder(Base):
    """兑换订单表"""
    __tablename__ = "redeem_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(32), unique=True, index=True, nullable=False, comment="订单号")
    openid = Column(String(64), index=True, nullable=False, comment="用户openid")
    product_id = Column(Integer, nullable=False, comment="商品ID")
    product_name = Column(String(100), nullable=False, comment="商品名称（快照）")
    points_cost = Column(Integer, nullable=False, comment="消耗积分（快照）")
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, comment="订单状态")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
