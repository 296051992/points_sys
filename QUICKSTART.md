# 快速使用指南

## 🚀 5分钟快速开始

### Windows 用户

```bash
# 双击运行或命令行执行
start.bat
```

服务会自动：
1. 安装依赖
2. 初始化数据库
3. 插入示例数据
4. 启动服务

访问：http://localhost:8000/docs

### Linux/Mac 用户

```bash
chmod +x start.sh
./start.sh
```

## 📝 管理员首次使用

### 1. 登录获取 Token

```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

保存返回的 `admin_token`。

### 2. 给用户加积分

```bash
# 方式1: 使用CLI工具（推荐）
python scripts/admin_cli.py add-points USER_OPENID 1000 --reason "新用户奖励"

# 方式2: 使用API
curl -X POST http://localhost:8000/admin/users/USER_OPENID/points-adjust \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"delta":1000,"reason":"新用户奖励"}'
```

### 3. 创建商品

```bash
# 方式1: 使用CLI工具
python scripts/admin_cli.py create-product "测试商品" 500 --stock 100

# 方式2: 使用API
curl -X POST http://localhost:8000/admin/products \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"测试商品",
    "points_cost":500,
    "stock":100,
    "is_active":1
  }'
```

### 4. 查看数据

```bash
# 查看系统统计
python scripts/view_db.py --stats

# 查看所有数据
python scripts/view_db.py --all

# 查看用户列表
python scripts/view_db.py --users

# 查看商品列表
python scripts/view_db.py --products

# 查看订单
python scripts/view_db.py --orders
```

## 🧪 测试和演示

### 生成测试数据

```bash
# 一键生成完整测试数据（10个用户，5个商品，15个订单）
python scripts/generate_test_data.py --all

# 或分步生成
python scripts/generate_test_data.py --users 10
python scripts/generate_test_data.py --products 5
python scripts/generate_test_data.py --orders 15
```

### 运行自动化测试

```bash
python scripts/test_api.py
```

这将自动测试：
- ✓ 健康检查
- ✓ 管理员登录
- ✓ 积分调整
- ✓ 商品管理
- ✓ 用户兑换流程

## 🔧 常用命令

### 管理员操作

```bash
# 给用户加积分
python scripts/admin_cli.py add-points USER_OPENID 1000

# 列出用户（按积分降序）
python scripts/admin_cli.py list-users --limit 20

# 列出积分大于500的用户
python scripts/admin_cli.py list-users --min-points 500

# 创建商品
python scripts/admin_cli.py create-product "商品名" 500 --stock 100

# 完成订单
python scripts/admin_cli.py fulfill-order ORDER_NO

# 取消订单并退款
python scripts/admin_cli.py cancel-order ORDER_NO
```

### 数据库操作

```bash
# 重新初始化数据库（会清空所有数据）
python scripts/init_db.py

# 插入初始商品
python scripts/seed.py

# 查看指定用户的积分流水
python scripts/view_db.py --ledger USER_OPENID
```

## 📱 小程序端使用流程

### 1. 用户登录

小程序调用 `wx.login()` 获取 code，然后：

```javascript
// 小程序端代码示例
wx.request({
  url: 'http://YOUR_API_URL/api/wx/login',
  method: 'POST',
  data: {
    code: code  // wx.login() 获取的 code
  },
  success: (res) => {
    const session_token = res.data.data.session_token;
    // 保存 token
    wx.setStorageSync('session_token', session_token);
  }
});
```

### 2. 查看个人信息

```javascript
wx.request({
  url: 'http://YOUR_API_URL/api/me',
  method: 'GET',
  header: {
    'Authorization': 'Bearer ' + wx.getStorageSync('session_token')
  },
  success: (res) => {
    console.log('积分余额:', res.data.data.points_balance);
  }
});
```

### 3. 查看商品列表

```javascript
wx.request({
  url: 'http://YOUR_API_URL/api/products',
  method: 'GET',
  success: (res) => {
    console.log('商品列表:', res.data.data.items);
  }
});
```

### 4. 兑换商品

```javascript
wx.request({
  url: 'http://YOUR_API_URL/api/redeem',
  method: 'POST',
  header: {
    'Authorization': 'Bearer ' + wx.getStorageSync('session_token')
  },
  data: {
    product_id: 1
  },
  success: (res) => {
    console.log('订单号:', res.data.data.order_no);
  }
});
```

### 5. 查看我的订单

```javascript
wx.request({
  url: 'http://YOUR_API_URL/api/me/orders',
  method: 'GET',
  header: {
    'Authorization': 'Bearer ' + wx.getStorageSync('session_token')
  },
  success: (res) => {
    console.log('我的订单:', res.data.data.items);
  }
});
```

## 🐛 故障排查

### 服务无法启动

1. 检查端口8000是否被占用
2. 确认Python版本 >= 3.11
3. 确认所有依赖已安装

### 数据库错误

1. 删除 `data.db` 文件
2. 重新运行 `python scripts/init_db.py`

### 认证失败

1. 确认 `.env` 文件存在且配置正确
2. 检查 token 是否正确传递
3. 确认 token 未过期（默认30天）

## 📞 获取帮助

查看完整文档：
- [README.md](README.md) - 完整项目文档
- [API_TESTS.md](API_TESTS.md) - API测试示例
- http://localhost:8000/docs - 在线API文档（启动服务后访问）
