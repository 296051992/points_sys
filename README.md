# 微信小程序积分兑换系统

基于 FastAPI + SQLite 的积分兑换系统后端 API，支持小程序端和管理端接口。

## 功能特性

- 🔐 微信登录认证（小程序端）
- 📊 积分管理（加分、扣分、兑换）
- 🛍️ 商品管理（CRUD、库存管理）
- 📦 订单管理（兑换、发货、取消、退款）
- 🔍 积分流水查询
- 👥 会员管理
- 🔒 JWT 认证保护

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- JWT (python-jose)
- Pydantic

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的微信小程序配置：

```env
WECHAT_APPID=your_wechat_appid
WECHAT_SECRET=your_wechat_secret
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
SECRET_KEY=your-secret-key-change-this-in-production
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 插入示例数据

```bash
python scripts/seed.py
```

### 5. 启动服务

```bash
uvicorn app.main:app --reload
```

服务将在 `http://localhost:8000` 启动。

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要接口

### 小程序端接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/wx/login | 微信登录 |
| GET | /api/me | 获取个人信息 |
| GET | /api/me/points-ledger | 积分明细 |
| GET | /api/products | 商品列表 |
| GET | /api/products/{id} | 商品详情 |
| POST | /api/redeem | 发起兑换 |
| GET | /api/me/orders | 我的订单 |

### 管理端接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /admin/login | 管理员登录 |
| GET | /admin/users | 会员列表 |
| GET | /admin/users/{openid}/points-ledger | 会员积分明细 |
| POST | /admin/users/{openid}/points-adjust | 加减积分 |
| POST | /admin/products | 创建商品 |
| PUT | /admin/products/{id} | 更新商品 |
| GET | /admin/products | 商品列表 |
| GET | /admin/orders | 订单列表 |
| PUT | /admin/orders/{order_no}/fulfill | 完成订单 |
| PUT | /admin/orders/{order_no}/cancel | 取消订单 |

## 数据库结构

### users (用户表)
- openid: 微信openid
- nickname: 昵称
- avatar_url: 头像
- points_balance: 积分余额

### points_ledger (积分流水表)
- openid: 用户openid
- delta: 积分变化量
- balance_after: 变化后余额
- type: 流水类型
- reason: 变化原因
- operator: 操作人

### products (商品表)
- name: 商品名称
- description: 商品描述
- image_url: 商品图片
- points_cost: 所需积分
- stock: 库存（-1表示无限）
- is_active: 是否上架

### redeem_orders (兑换订单表)
- order_no: 订单号
- openid: 用户openid
- product_id: 商品ID
- product_name: 商品名称（快照）
- points_cost: 消耗积分（快照）
- status: 订单状态

## 核心业务逻辑

### 积分兑换流程

1. 用户发起兑换请求
2. 系统检查积分余额
3. 系统检查商品库存
4. 扣减库存（如果不是无限库存）
5. 扣减用户积分
6. 写入积分流水
7. 生成兑换订单
8. 返回订单信息

所有操作在数据库事务中完成，保证数据一致性。

### 事务保证

使用 SQLAlchemy 的事务机制和行级锁（`with_for_update()`）确保并发安全。

### 防止余额为负

- 兑换前检查 `user.points_balance >= product.points_cost`
- 管理端扣分前检查 `user.points_balance + delta >= 0`

## 管理工具

### 数据库查看工具

```bash
# 查看系统统计
python scripts/view_db.py --stats

# 查看所有数据
python scripts/view_db.py --all

# 查看用户列表
python scripts/view_db.py --users

# 查看商品列表
python scripts/view_db.py --products

# 查看订单列表
python scripts/view_db.py --orders

# 查看积分流水（所有用户）
python scripts/view_db.py --ledger

# 查看指定用户的积分流水
python scripts/view_db.py --ledger test_user_001
```

### 测试数据生成器

```bash
# 生成所有测试数据
python scripts/generate_test_data.py --all

# 生成10个测试用户
python scripts/generate_test_data.py --users 10

# 生成5个测试商品
python scripts/generate_test_data.py --products 5

# 生成20个测试订单
python scripts/generate_test_data.py --orders 20
```

### 管理员CLI工具

```bash
# 给用户加积分
python scripts/admin_cli.py add-points test_user_001 1000 --reason "活动奖励"

# 创建商品
python scripts/admin_cli.py create-product "新商品" 500 --description "商品描述" --stock 100

# 列出用户
python scripts/admin_cli.py list-users --limit 20 --min-points 500

# 完成订单
python scripts/admin_cli.py fulfill-order R20260127120000ABCD1234

# 取消订单并退款
python scripts/admin_cli.py cancel-order R20260127120000ABCD1234
```

### API自动化测试

```bash
# 运行完整API测试
python scripts/test_api.py
```

## 测试建议

1. **使用自动化测试**
```bash
python scripts/test_api.py
```

2. **生成测试数据**
```bash
python scripts/generate_test_data.py --all
```

3. **手动测试**
```bash
# 管理员登录
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

详细的API测试示例请查看 [API_TESTS.md](API_TESTS.md)

## Docker 部署

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker

```bash
# 构建镜像
docker build -t points-system .

# 运行容器
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/.env:/app/.env \
  --name points-api \
  points-system
```

## 生产部署注意事项

1. 修改 `.env` 中的 `SECRET_KEY` 为随机字符串
2. 修改默认管理员密码
3. 配置真实的微信小程序 APPID 和 SECRET
4. 配置 CORS 允许的具体域名（修改 app/main.py）
5. 使用生产级数据库（PostgreSQL/MySQL）替代 SQLite
6. 启用 HTTPS
7. 配置日志记录和日志轮转
8. 添加监控和告警
9. 配置 API 速率限制
10. 定期备份数据库

## 项目结构

```
minig/
├── app/                      # 应用主目录
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── db.py                # 数据库连接
│   ├── models.py            # 数据模型
│   ├── schemas.py           # API 数据结构
│   ├── auth.py              # JWT 认证
│   ├── services/            # 业务逻辑层
│   │   ├── points.py        # 积分服务
│   │   └── wechat.py        # 微信服务
│   └── routers/             # 路由层
│       ├── api.py           # 小程序端接口
│       └── admin.py         # 管理端接口
├── scripts/                 # 工具脚本
│   ├── init_db.py           # 初始化数据库
│   ├── seed.py              # 插入示例数据
│   ├── view_db.py           # 数据库查看工具
│   ├── generate_test_data.py # 测试数据生成器
│   ├── admin_cli.py         # 管理员CLI工具
│   └── test_api.py          # API自动化测试
├── .env.example             # 配置模板
├── .env                     # 实际配置
├── .gitignore               # Git忽略文件
├── requirements.txt         # Python依赖
├── Dockerfile               # Docker配置
├── docker-compose.yml       # Docker Compose配置
├── start.bat                # Windows启动脚本
├── start.sh                 # Linux/Mac启动脚本
├── README.md                # 项目文档
└── API_TESTS.md             # API测试文档
```

## 常见问题

### 1. 依赖安装失败
确保使用 Python 3.11+ 版本，并升级 pip：
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 数据库初始化失败
检查是否有文件权限问题，确保当前目录可写。

### 3. 微信登录失败
确保 `.env` 文件中配置了正确的 `WECHAT_APPID` 和 `WECHAT_SECRET`。

### 4. JWT 认证失败
检查 `SECRET_KEY` 是否正确配置，token 是否已过期。

## 许可证

MIT
