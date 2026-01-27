from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # 微信小程序配置
    WECHAT_APPID: str
    WECHAT_SECRET: str

    # 管理员账号
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # 数据库配置
    DB_PATH: str = "./data.db"

    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 2592000  # 30天

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
