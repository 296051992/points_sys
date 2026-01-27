"""
种子数据脚本
插入示例商品数据
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import Product


def main():
    """插入种子数据"""
    db = SessionLocal()

    try:
        # 检查是否已有商品
        existing_count = db.query(Product).count()
        if existing_count > 0:
            print(f"数据库中已有 {existing_count} 个商品，跳过种子数据插入。")
            return

        print("开始插入种子数据...")

        # 创建示例商品
        products = [
            Product(
                name="星巴克咖啡券",
                description="星巴克中杯咖啡兑换券一张，适用于全国门店",
                image_url="https://example.com/starbucks.jpg",
                points_cost=500,
                stock=100,
                is_active=1
            ),
            Product(
                name="精美笔记本",
                description="A5 尺寸精装笔记本，适合办公学习",
                image_url="https://example.com/notebook.jpg",
                points_cost=300,
                stock=50,
                is_active=1
            ),
            Product(
                name="10元话费充值",
                description="中国移动/联通/电信 10元话费直充",
                image_url="https://example.com/mobile.jpg",
                points_cost=100,
                stock=-1,  # 无限库存
                is_active=1
            )
        ]

        for product in products:
            db.add(product)

        db.commit()
        print(f"成功插入 {len(products)} 个示例商品！")

        # 显示商品信息
        print("\n商品列表：")
        for i, product in enumerate(products, 1):
            stock_info = "无限" if product.stock == -1 else str(product.stock)
            print(f"{i}. {product.name} - {product.points_cost}积分 (库存: {stock_info})")

    except Exception as e:
        print(f"插入种子数据失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
