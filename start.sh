#!/bin/bash
# Linux/Mac 启动脚本

echo "========================================"
echo "微信小程序积分兑换系统 - 快速启动"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python 3.11+"
    exit 1
fi

echo "[1/5] 检查依赖..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[信息] 检测到依赖未安装，开始安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
else
    echo "[完成] 依赖已安装"
fi

echo ""
echo "[2/5] 检查配置文件..."
if [ ! -f .env ]; then
    echo "[信息] .env 不存在，从模板复制..."
    cp .env.example .env
    echo "[警告] 请编辑 .env 文件填入微信小程序配置"
fi
echo "[完成] 配置文件就绪"

echo ""
echo "[3/5] 初始化数据库..."
python3 scripts/init_db.py
if [ $? -ne 0 ]; then
    echo "[错误] 数据库初始化失败"
    exit 1
fi

echo ""
echo "[4/5] 插入示例数据..."
python3 scripts/seed.py

echo ""
echo "[5/5] 启动服务..."
echo ""
echo "========================================"
echo "服务启动中..."
echo "访问: http://localhost:8000/docs"
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

uvicorn app.main:app --reload
