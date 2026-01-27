from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import get_db
from app.auth import get_current_openid, create_access_token
from app.models import User, Product, RedeemOrder, OrderStatus
from app.schemas import (
    ApiResponse, WxLoginRequest, WxLoginResponse, UserInfo,
    PointsLedgerList, ProductList, ProductInfo, RedeemRequest,
    OrderInfo, OrderList, PointsLedgerItem
)
from app.services.wechat import jscode2session, WeChatError
from app.services.points import (
    redeem_product, get_ledger,
    InsufficientPointsError, OutOfStockError, ProductNotFoundError, ProductNotActiveError
)

router = APIRouter(prefix="/api", tags=["小程序端"])


@router.post("/wx/login", response_model=ApiResponse)
async def wx_login(request: WxLoginRequest, db: Session = Depends(get_db)):
    """微信登录"""
    try:
        # 调用微信接口获取 openid
        wx_data = await jscode2session(request.code)
        openid = wx_data["openid"]

        # 查找或创建用户
        user = db.query(User).filter(User.openid == openid).first()
        if not user:
            user = User(openid=openid)
            db.add(user)
            db.commit()
            db.refresh(user)

        # 生成 session_token
        token = create_access_token(data={"sub": openid, "type": "user"})

        return ApiResponse(
            data=WxLoginResponse(
                session_token=token,
                openid=openid
            )
        )
    except WeChatError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=ApiResponse)
def get_me(openid: str = Depends(get_current_openid), db: Session = Depends(get_db)):
    """获取个人信息"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return ApiResponse(data=UserInfo.model_validate(user))


@router.get("/me/points-ledger", response_model=ApiResponse)
def get_my_points_ledger(
    page: int = 1,
    page_size: int = 20,
    openid: str = Depends(get_current_openid),
    db: Session = Depends(get_db)
):
    """获取积分明细"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    ledgers, total = get_ledger(db, openid, page, page_size)

    return ApiResponse(
        data=PointsLedgerList(
            items=[PointsLedgerItem.model_validate(l) for l in ledgers],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.get("/products", response_model=ApiResponse)
def get_products(db: Session = Depends(get_db)):
    """获取商品列表（仅上架商品）"""
    products = db.query(Product).filter(Product.is_active == 1).order_by(desc(Product.created_at)).all()

    return ApiResponse(
        data=ProductList(
            items=[ProductInfo.model_validate(p) for p in products]
        )
    )


@router.get("/products/{product_id}", response_model=ApiResponse)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """获取商品详情"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    return ApiResponse(data=ProductInfo.model_validate(product))


@router.post("/redeem", response_model=ApiResponse)
def redeem(
    request: RedeemRequest,
    openid: str = Depends(get_current_openid),
    db: Session = Depends(get_db)
):
    """发起兑换"""
    try:
        order = redeem_product(db, openid, request.product_id)
        return ApiResponse(data=OrderInfo.model_validate(order))
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProductNotActiveError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientPointsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/orders", response_model=ApiResponse)
def get_my_orders(
    page: int = 1,
    page_size: int = 20,
    openid: str = Depends(get_current_openid),
    db: Session = Depends(get_db)
):
    """获取我的订单"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    query = db.query(RedeemOrder).filter(RedeemOrder.openid == openid)
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
