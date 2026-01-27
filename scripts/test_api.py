"""
简易API测试工具
可以快速测试主要接口功能
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.admin_token: Optional[str] = None
        self.user_token: Optional[str] = None
        self.test_openid = "test_user_api_001"

    def test_health(self):
        """测试健康检查"""
        print("\n[测试] 健康检查")
        try:
            resp = requests.get(f"{self.base_url}/health")
            if resp.status_code == 200:
                print_success(f"健康检查通过: {resp.json()}")
                return True
            else:
                print_error(f"健康检查失败: {resp.status_code}")
                return False
        except Exception as e:
            print_error(f"连接失败: {e}")
            print_warning("请确保服务已启动: uvicorn app.main:app --reload")
            return False

    def test_admin_login(self):
        """测试管理员登录"""
        print("\n[测试] 管理员登录")
        try:
            resp = requests.post(
                f"{self.base_url}/admin/login",
                json={"username": "admin", "password": "admin123"}
            )
            if resp.status_code == 200:
                data = resp.json()
                self.admin_token = data["data"]["admin_token"]
                print_success(f"登录成功: {data['data']['username']}")
                print_info(f"Token: {self.admin_token[:30]}...")
                return True
            else:
                print_error(f"登录失败: {resp.text}")
                return False
        except Exception as e:
            print_error(f"登录异常: {e}")
            return False

    def test_adjust_points(self):
        """测试积分调整"""
        print("\n[测试] 积分调整")
        if not self.admin_token:
            print_warning("需要先登录")
            return False

        try:
            # 加积分
            resp = requests.post(
                f"{self.base_url}/admin/users/{self.test_openid}/points-adjust",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={"delta": 1000, "reason": "测试充值"}
            )
            if resp.status_code == 200:
                data = resp.json()
                print_success(f"加分成功: 余额={data['data']['balance_after']}")
            else:
                print_error(f"加分失败: {resp.text}")
                return False

            # 扣积分
            resp = requests.post(
                f"{self.base_url}/admin/users/{self.test_openid}/points-adjust",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={"delta": -100, "reason": "测试扣分"}
            )
            if resp.status_code == 200:
                data = resp.json()
                print_success(f"扣分成功: 余额={data['data']['balance_after']}")
                return True
            else:
                print_error(f"扣分失败: {resp.text}")
                return False
        except Exception as e:
            print_error(f"积分调整异常: {e}")
            return False

    def test_products(self):
        """测试商品接口"""
        print("\n[测试] 商品管理")
        if not self.admin_token:
            print_warning("需要先登录")
            return False

        try:
            # 创建商品
            resp = requests.post(
                f"{self.base_url}/admin/products",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                json={
                    "name": "API测试商品",
                    "description": "通过API创建的测试商品",
                    "points_cost": 200,
                    "stock": 50,
                    "is_active": 1
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                product_id = data["data"]["id"]
                print_success(f"创建商品成功: ID={product_id}, 名称={data['data']['name']}")

                # 更新商品
                resp = requests.put(
                    f"{self.base_url}/admin/products/{product_id}",
                    headers={"Authorization": f"Bearer {self.admin_token}"},
                    json={"points_cost": 250}
                )
                if resp.status_code == 200:
                    print_success("更新商品成功")
                    return True
                else:
                    print_error(f"更新商品失败: {resp.text}")
                    return False
            else:
                print_error(f"创建商品失败: {resp.text}")
                return False
        except Exception as e:
            print_error(f"商品管理异常: {e}")
            return False

    def test_user_flow(self):
        """测试用户兑换流程"""
        print("\n[测试] 用户兑换流程")

        # 创建用户token（模拟登录）
        try:
            from app.auth import create_access_token
            self.user_token = create_access_token({"sub": self.test_openid, "type": "user"})
            print_info(f"生成用户Token: {self.user_token[:30]}...")
        except Exception as e:
            print_error(f"生成Token失败: {e}")
            return False

        try:
            # 查看个人信息
            resp = requests.get(
                f"{self.base_url}/api/me",
                headers={"Authorization": f"Bearer {self.user_token}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                print_success(f"个人信息: 余额={data['data']['points_balance']}分")
            else:
                print_error(f"获取个人信息失败: {resp.text}")
                return False

            # 查看商品列表
            resp = requests.get(f"{self.base_url}/api/products")
            if resp.status_code == 200:
                data = resp.json()
                products = data["data"]["items"]
                print_success(f"商品列表: 共{len(products)}个商品")

                if products:
                    # 兑换第一个商品
                    product = products[0]
                    print_info(f"尝试兑换: {product['name']} ({product['points_cost']}分)")

                    resp = requests.post(
                        f"{self.base_url}/api/redeem",
                        headers={"Authorization": f"Bearer {self.user_token}"},
                        json={"product_id": product["id"]}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        print_success(f"兑换成功: 订单号={data['data']['order_no']}")

                        # 查看订单
                        resp = requests.get(
                            f"{self.base_url}/api/me/orders",
                            headers={"Authorization": f"Bearer {self.user_token}"}
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            print_success(f"我的订单: 共{data['data']['total']}个订单")
                            return True
                    else:
                        print_error(f"兑换失败: {resp.text}")
                        return False
            else:
                print_error(f"获取商品列表失败: {resp.text}")
                return False
        except Exception as e:
            print_error(f"用户流程异常: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("微信小程序积分兑换系统 - API 测试")
        print("=" * 60)

        tests = [
            ("健康检查", self.test_health),
            ("管理员登录", self.test_admin_login),
            ("积分调整", self.test_adjust_points),
            ("商品管理", self.test_products),
            ("用户流程", self.test_user_flow),
        ]

        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print_error(f"{name} 执行异常: {e}")
                results.append((name, False))

        # 总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "通过" if result else "失败"
            color = Colors.GREEN if result else Colors.RED
            print(f"{color}{status:4s}{Colors.END} - {name}")

        print(f"\n总计: {passed}/{total} 通过")

        if passed == total:
            print_success("所有测试通过！")
        else:
            print_warning(f"有 {total - passed} 个测试失败")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
