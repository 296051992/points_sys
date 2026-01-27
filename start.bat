@echo off
REM Windows 批处理脚本 - 快速启动系统

echo ========================================
echo 微信小程序积分兑换系统 - 快速启动
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

echo [1/5] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [信息] 检测到依赖未安装，开始安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [完成] 依赖已安装
)

echo.
echo [2/5] 检查配置文件...
if not exist .env (
    echo [信息] .env 不存在，从模板复制...
    copy .env.example .env
    echo [警告] 请编辑 .env 文件填入微信小程序配置
)
echo [完成] 配置文件就绪

echo.
echo [3/5] 初始化数据库...
python scripts\init_db.py
if errorlevel 1 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo [4/5] 插入示例数据...
python scripts\seed.py
if errorlevel 1 (
    echo [警告] 示例数据插入失败（可能已存在）
)

echo.
echo [5/5] 启动服务...
echo.
echo ========================================
echo 服务启动中...
echo 访问: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

uvicorn app.main:app --reload
