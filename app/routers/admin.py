from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from app.db import get_db
from app.auth import get_admin_user, create_access_token
from app.config import settings
from app.models import User, Product, RedeemOrder, OrderStatus
from app.schemas import (
    ApiResponse, AdminLoginRequest, AdminLoginResponse,
    UserList, UserListItem, PointsAdjustRequest, PointsLedgerItem,
    ProductCreateRequest, ProductUpdateRequest, ProductInfo, ProductList,
    OrderList, OrderInfo, OrderCancelRequest, PointsLedgerList
)
from app.services.points import (
    adjust_points, get_ledger, cancel_order_with_refund,
    InsufficientPointsError
)

router = APIRouter(prefix="/admin", tags=["管理端"])


@router.post("/login", response_model=ApiResponse)
def admin_login(request: AdminLoginRequest):
    """管理员登录"""
    if request.username != settings.ADMIN_USERNAME or request.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 admin_token
    token = create_access_token(data={"sub": request.username, "type": "admin"})

    return ApiResponse(
        data=AdminLoginResponse(
            admin_token=token,
            username=request.username
        )
    )


@router.get("/users", response_model=ApiResponse)
def get_users(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取会员列表"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = db.query(User)

    # 搜索
    if keyword:
        query = query.filter(
            or_(
                User.openid.contains(keyword),
                User.nickname.contains(keyword)
            )
        )

    total = query.count()
    users = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return ApiResponse(
        data=UserList(
            items=[UserListItem.model_validate(u) for u in users],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.get("/users/{openid}/points-ledger", response_model=ApiResponse)
def get_user_points_ledger(
    openid: str,
    page: int = 1,
    page_size: int = 20,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取会员积分明细"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    # 检查用户是否存在
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    ledgers, total = get_ledger(db, openid, page, page_size)

    return ApiResponse(
        data=PointsLedgerList(
            items=[PointsLedgerItem.model_validate(l) for l in ledgers],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.post("/users/{openid}/points-adjust", response_model=ApiResponse)
def adjust_user_points(
    openid: str,
    request: PointsAdjustRequest,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """调整会员积分"""
    try:
        ledger = adjust_points(
            db=db,
            openid=openid,
            delta=request.delta,
            reason=request.reason,
            operator=admin
        )
        return ApiResponse(data=PointsLedgerItem.model_validate(ledger))
    except InsufficientPointsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/products", response_model=ApiResponse)
def create_product(
    request: ProductCreateRequest,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建商品"""
    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    return ApiResponse(data=ProductInfo.model_validate(product))


@router.put("/products/{product_id}", response_model=ApiResponse)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新商品"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 更新字段
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    return ApiResponse(data=ProductInfo.model_validate(product))


@router.get("/products", response_model=ApiResponse)
def get_all_products(
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有商品（包含下架）"""
    products = db.query(Product).order_by(desc(Product.created_at)).all()

    return ApiResponse(
        data=ProductList(
            items=[ProductInfo.model_validate(p) for p in products]
        )
    )


@router.get("/orders", response_model=ApiResponse)
def get_orders(
    page: int = 1,
    page_size: int = 20,
    status: OrderStatus = None,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = db.query(RedeemOrder)

    # 按状态筛选
    if status:
        query = query.filter(RedeemOrder.status == status)

    total = query.count()
    orders = query.order_by(desc(RedeemOrder.created_at)).offset((page - 1) * page_size).limit(page_size).all()

    return ApiResponse(
        data=OrderList(
            items=[OrderInfo.model_validate(o) for o in orders],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.put("/orders/{order_no}/fulfill", response_model=ApiResponse)
def fulfill_order(
    order_no: str,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """完成订单（发货）"""
    order = db.query(RedeemOrder).filter(RedeemOrder.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能完成待发货订单")

    order.status = OrderStatus.FULFILLED
    db.commit()
    db.refresh(order)

    return ApiResponse(data=OrderInfo.model_validate(order))


@router.put("/orders/{order_no}/cancel", response_model=ApiResponse)
def cancel_order(
    order_no: str,
    request: OrderCancelRequest,
    admin: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """取消订单"""
    try:
        if request.refund:
            order = cancel_order_with_refund(db, order_no, admin)
        else:
            order = db.query(RedeemOrder).filter(RedeemOrder.order_no == order_no).first()
            if not order:
                raise HTTPException(status_code=404, detail="订单不存在")

            if order.status != OrderStatus.PENDING:
                raise HTTPException(status_code=400, detail="只能取消待发货订单")

            order.status = OrderStatus.CANCELLED
            db.commit()
            db.refresh(order)

        return ApiResponse(data=OrderInfo.model_validate(order))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
