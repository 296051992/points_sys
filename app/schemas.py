from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models import PointsLedgerType, OrderStatus


# 统一响应格式
class ApiResponse(BaseModel):
    """API 统一响应格式"""
    code: int = 0
    msg: str = "ok"
    data: Any = None


# 小程序端 - 登录
class WxLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录码")


class WxLoginResponse(BaseModel):
    """微信登录响应"""
    session_token: str = Field(..., description="会话token")
    openid: str = Field(..., description="用户openid")


# 用户信息
class UserInfo(BaseModel):
    """用户信息"""
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    points_balance: int
    created_at: datetime

    class Config:
        from_attributes = True


# 积分流水
class PointsLedgerItem(BaseModel):
    """积分流水项"""
    id: int
    delta: int
    balance_after: int
    type: PointsLedgerType
    reason: str
    operator: str
    ref_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PointsLedgerList(BaseModel):
    """积分流水列表"""
    items: List[PointsLedgerItem]
    total: int
    page: int
    page_size: int


# 商品
class ProductInfo(BaseModel):
    """商品信息"""
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    points_cost: int
    stock: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    """商品列表"""
    items: List[ProductInfo]


# 兑换
class RedeemRequest(BaseModel):
    """兑换请求"""
    product_id: int = Field(..., description="商品ID")


class OrderInfo(BaseModel):
    """订单信息"""
    id: int
    order_no: str
    openid: str
    product_id: int
    product_name: str
    points_cost: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """订单列表"""
    items: List[OrderInfo]
    total: int
    page: int
    page_size: int


# 管理端 - 登录
class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    admin_token: str
    username: str


# 管理端 - 用户列表
class UserListItem(BaseModel):
    """用户列表项"""
    id: int
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    points_balance: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """用户列表"""
    items: List[UserListItem]
    total: int
    page: int
    page_size: int


# 管理端 - 积分调整
class PointsAdjustRequest(BaseModel):
    """积分调整请求"""
    delta: int = Field(..., description="积分变化量（正数加分，负数扣分）")
    reason: str = Field(..., description="调整原因")


# 管理端 - 商品创建/更新
class ProductCreateRequest(BaseModel):
    """商品创建请求"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    points_cost: int = Field(..., gt=0)
    stock: int = Field(default=-1, description="库存（-1表示无限）")
    is_active: int = Field(default=1, description="是否上架（1上架，0下架）")


class ProductUpdateRequest(BaseModel):
    """商品更新请求"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    points_cost: Optional[int] = Field(None, gt=0)
    stock: Optional[int] = None
    is_active: Optional[int] = None


# 管理端 - 订单操作
class OrderCancelRequest(BaseModel):
    """订单取消请求"""
    refund: bool = Field(default=True, description="是否退款")
