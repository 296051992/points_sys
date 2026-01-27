# API 测试示例

本文档提供了测试各个接口的 curl 命令示例。

## 环境变量

```bash
# 设置基础URL
export API_BASE=http://localhost:8000
```

## 1. 健康检查

```bash
curl $API_BASE/health
```

## 2. 管理端接口测试

### 2.1 管理员登录

```bash
curl -X POST $API_BASE/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

响应示例：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "admin"
  }
}
```

**将返回的 admin_token 保存到环境变量：**
```bash
export ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2.2 查看会员列表

```bash
curl -X GET "$API_BASE/admin/users?page=1&page_size=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2.3 给用户加积分

```bash
# 先创建一个测试用户的openid
export TEST_OPENID="test_user_openid_001"

# 给用户加1000积分
curl -X POST "$API_BASE/admin/users/$TEST_OPENID/points-adjust" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delta": 1000,
    "reason": "新用户注册奖励"
  }'
```

### 2.4 扣除积分

```bash
curl -X POST "$API_BASE/admin/users/$TEST_OPENID/points-adjust" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delta": -50,
    "reason": "违规扣分"
  }'
```

### 2.5 查看用户积分流水

```bash
curl -X GET "$API_BASE/admin/users/$TEST_OPENID/points-ledger?page=1&page_size=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2.6 创建商品

```bash
curl -X POST "$API_BASE/admin/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试商品",
    "description": "这是一个测试商品",
    "image_url": "https://example.com/test.jpg",
    "points_cost": 200,
    "stock": 50,
    "is_active": 1
  }'
```

### 2.7 更新商品

```bash
# 假设商品ID为1
curl -X PUT "$API_BASE/admin/products/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的商品名称",
    "points_cost": 250
  }'
```

### 2.8 查看所有商品（包含下架）

```bash
curl -X GET "$API_BASE/admin/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2.9 查看订单列表

```bash
# 查看所有订单
curl -X GET "$API_BASE/admin/orders?page=1&page_size=20" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 筛选待发货订单
curl -X GET "$API_BASE/admin/orders?page=1&page_size=20&status=PENDING" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2.10 完成订单（发货）

```bash
# 假设订单号为 R20260127120000ABCD1234
export ORDER_NO="R20260127120000ABCD1234"

curl -X PUT "$API_BASE/admin/orders/$ORDER_NO/fulfill" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 2.11 取消订单（带退款）

```bash
curl -X PUT "$API_BASE/admin/orders/$ORDER_NO/cancel" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refund": true
  }'
```

## 3. 小程序端接口测试

### 3.1 模拟微信登录

**注意：** 实际环境需要真实的微信登录码，这里仅用于测试结构。在测试环境，可以直接创建用户token。

```bash
# 直接创建一个测试用户token（仅测试用）
# 在生产环境应该调用 POST /api/wx/login

# 使用管理员加分时创建的测试用户
export USER_TOKEN="<从管理端登录获取或手动生成>"
```

手动生成测试token的Python代码：
```python
from app.auth import create_access_token
token = create_access_token({"sub": "test_user_openid_001", "type": "user"})
print(token)
```

### 3.2 获取个人信息

```bash
curl -X GET "$API_BASE/api/me" \
  -H "Authorization: Bearer $USER_TOKEN"
```

### 3.3 查看积分流水

```bash
curl -X GET "$API_BASE/api/me/points-ledger?page=1&page_size=20" \
  -H "Authorization: Bearer $USER_TOKEN"
```

### 3.4 查看商品列表

```bash
curl -X GET "$API_BASE/api/products"
```

### 3.5 查看商品详情

```bash
# 假设商品ID为1
curl -X GET "$API_BASE/api/products/1"
```

### 3.6 兑换商品

```bash
# 兑换ID为1的商品
curl -X POST "$API_BASE/api/redeem" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1
  }'
```

### 3.7 查看我的订单

```bash
curl -X GET "$API_BASE/api/me/orders?page=1&page_size=20" \
  -H "Authorization: Bearer $USER_TOKEN"
```

## 4. 完整测试流程

### 场景：用户兑换商品流程

```bash
# 1. 管理员登录
ADMIN_RESP=$(curl -s -X POST $API_BASE/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')
ADMIN_TOKEN=$(echo $ADMIN_RESP | jq -r '.data.admin_token')
echo "管理员Token: $ADMIN_TOKEN"

# 2. 给测试用户加积分
TEST_OPENID="test_user_001"
curl -X POST "$API_BASE/admin/users/$TEST_OPENID/points-adjust" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delta":1000,"reason":"测试充值"}'

# 3. 创建测试商品
PRODUCT_RESP=$(curl -s -X POST "$API_BASE/admin/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试商品","points_cost":500,"stock":10,"is_active":1}')
PRODUCT_ID=$(echo $PRODUCT_RESP | jq -r '.data.id')
echo "商品ID: $PRODUCT_ID"

# 4. 生成用户token（需要Python环境）
# python3 -c "from app.auth import create_access_token; print(create_access_token({'sub':'$TEST_OPENID','type':'user'}))"

# 5. 用户查看商品列表
curl -X GET "$API_BASE/api/products"

# 6. 用户兑换商品
# curl -X POST "$API_BASE/api/redeem" \
#   -H "Authorization: Bearer $USER_TOKEN" \
#   -H "Content-Type: application/json" \
#   -d "{\"product_id\":$PRODUCT_ID}"

# 7. 管理员查看订单
curl -X GET "$API_BASE/admin/orders" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 5. 错误场景测试

### 5.1 积分不足兑换

```bash
# 先扣除用户积分至不足
curl -X POST "$API_BASE/admin/users/$TEST_OPENID/points-adjust" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delta":-900,"reason":"测试扣分"}'

# 尝试兑换（应该失败）
curl -X POST "$API_BASE/api/redeem" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1}'
```

### 5.2 库存不足

```bash
# 更新商品库存为0
curl -X PUT "$API_BASE/admin/products/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stock":0}'

# 尝试兑换（应该失败）
curl -X POST "$API_BASE/api/redeem" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1}'
```

### 5.3 未授权访问

```bash
# 不带token访问需要认证的接口
curl -X GET "$API_BASE/api/me"
# 应返回 401 错误

# 使用错误的token
curl -X GET "$API_BASE/api/me" \
  -H "Authorization: Bearer invalid_token_here"
# 应返回 401 错误
```

## 6. 注意事项

1. **jq工具**: 部分命令使用了 `jq` 来解析JSON，请先安装：
   - Ubuntu/Debian: `sudo apt-get install jq`
   - macOS: `brew install jq`
   - Windows: 下载 https://stedolan.github.io/jq/

2. **换行符**: Windows用户如果使用PowerShell，需要将 `\` 改为 `` ` ``

3. **编码**: 确保终端支持UTF-8编码以正确显示中文

4. **生产环境**: 以上示例仅用于开发测试，生产环境务必：
   - 使用HTTPS
   - 修改默认密码
   - 配置合适的CORS策略
   - 启用请求限流
