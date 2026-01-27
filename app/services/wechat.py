import httpx
from app.config import settings


class WeChatError(Exception):
    """微信接口错误"""
    pass


async def jscode2session(code: str) -> dict:
    """
    调用微信 jscode2session 接口

    Args:
        code: 小程序登录码

    Returns:
        包含 openid 和 session_key 的字典

    Raises:
        WeChatError: 微信接口调用失败
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # 检查是否有错误码
            if "errcode" in data and data["errcode"] != 0:
                raise WeChatError(f"微信登录失败: {data.get('errmsg', '未知错误')}")

            # 检查是否包含必要字段
            if "openid" not in data:
                raise WeChatError("微信接口返回数据格式错误")

            return data

        except httpx.HTTPError as e:
            raise WeChatError(f"网络请求失败: {str(e)}")
