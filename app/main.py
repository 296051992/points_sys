from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import api, admin

# 创建 FastAPI 应用
app = FastAPI(
    title="微信小程序积分兑换系统",
    description="基于 FastAPI 的积分兑换系统后端 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api.router)
app.include_router(admin.router)

# 挂载静态文件
import os
current_dir = os.path.dirname(__file__)  # app目录
project_root = os.path.dirname(current_dir)  # 项目根目录
static_dir = os.path.join(project_root, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}


@app.get("/admin")
async def admin_page():
    """管理后台页面"""
    return {"message": "管理后台页面", "url": "/static/admin/index.html"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "微信小程序积分兑换系统 API",
        "docs": "/docs",
        "health": "/health"
    }
