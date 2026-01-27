"""
初始化数据库脚本
运行此脚本将创建所有数据表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db


def main():
    """初始化数据库"""
    print("开始初始化数据库...")
    init_db()
    print("数据库初始化完成！")
    print("所有表已创建成功。")


if __name__ == "__main__":
    main()
