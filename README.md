# FastAPI 企业级后端服务

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

一个基于 FastAPI 构建的企业级后端服务，提供完整的用户管理、支付系统、内容管理和权限控制功能。

## ✨ 特性

- 🚀 **高性能**: 基于 FastAPI 和异步编程，支持高并发请求
- 🔐 **安全认证**: JWT Token 认证，完整的权限管理系统
- 💳 **支付集成**: 支持微信支付、支付宝等多种支付方式
- 📊 **数据管理**: SQLAlchemy ORM，Alembic 数据库迁移
- ⚡ **异步任务**: Celery 分布式任务队列
- 📝 **自动文档**: OpenAPI 3.0 自动生成 API 文档
- 🐳 **容器化**: Docker 容器化部署，支持多环境配置
- 🧪 **代码质量**: 完整的测试覆盖和代码检查

## 🛠 技术栈

### 核心框架
- **[FastAPI](https://fastapi.tiangolo.com/)** - 现代、快速的 Web 框架
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - 数据验证和设置管理
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL 工具包和 ORM
- **[Alembic](https://alembic.sqlalchemy.org/)** - 数据库迁移工具

### 数据存储
- **MySQL 8.0+** - 主数据库
- **Redis 7.2+** - 缓存和会话存储

### 异步任务
- **[Celery](https://docs.celeryq.dev/)** - 分布式任务队列
- **Redis** - Celery 消息代理

### 开发工具
- **Docker** - 容器化部署
- **Nginx** - 反向代理和静态文件服务
- **Pytest** - 测试框架

## 🚀 快速开始

### 环境要求

- Python 3.12+
- MySQL 8.0+
- Redis 7.2+
- Docker (可选)

### 本地开发

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd fastapi
   ```

2. **配置环境**
   ```bash
   # 复制配置文件
   cp .env.example .env
   cp config.example.yaml config.yaml
   
   # 编辑配置文件，设置数据库连接等
   vim config.yaml
   ```

3. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # 或 .venv\Scripts\activate  # Windows
   ```

4. **安装依赖**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **启动服务依赖 (使用 Docker)**
   ```bash
   docker compose -f docker-compose-dev.yml up -d
   ```

6. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

7. **初始化数据**
   ```bash
   python app/utils/init_permissions.py
   python app/utils/init_role.py
   python app/utils/init_user.py
   python app/utils/init_city.py
   python app/utils/init_payment_channel.py
   ```

8. **启动应用**
   ```bash
   python start.py
   ```

访问 http://localhost:8000/docs 查看 API 文档。

### Docker 部署

1. **准备配置文件**
   ```bash
   cp .env.example .env
   cp config.example.yaml config.yaml
   # 编辑配置文件
   ```

2. **选择部署方式**
   ```bash
   # 完整部署 (包含所有服务)
   docker compose -f docker-compose-full.yml up -d --build
   
   # 仅 API 服务 (外部数据库)
   docker compose -f docker-compose.yml up -d --build
   
   # 仅 Celery 任务队列
   docker compose -f docker-compose-celery.yml up -d --build
   ```

3. **执行数据库迁移**
   ```bash
   docker exec -it <container-name>-server-1 bash
   alembic upgrade head
   # 执行初始化脚本...
   ```

## 📁 项目结构

```
fastapi/
├── app/                    # 应用主目录
│   ├── alembic/           # 数据库迁移文件
│   ├── api/               # API 路由
│   │   ├── backend/       # 后台管理 API
│   │   ├── frontend/      # 前端 API
│   │   └── routes/        # 通用路由
│   ├── constants/         # 常量定义
│   ├── core/              # 核心组件 (数据库、缓存、安全等)
│   ├── models/            # SQLAlchemy 数据模型
│   ├── schemas/           # Pydantic 数据模式
│   ├── services/          # 业务逻辑服务层
│   ├── tasks/             # Celery 异步任务
│   └── utils/             # 工具函数
├── docker/                # Docker 配置文件
├── public/                # 静态文件目录
├── scripts/               # 辅助脚本
├── volumes/               # Docker 数据卷
├── requirements.txt       # Python 依赖
├── config.yaml           # 应用配置文件
└── main.py               # 应用入口点
```

## 📖 开发指南

### API 开发规范

本项目遵循 RESTful API 设计原则：

#### 接口命名约定
- 使用复数名词：`/api/v1/backend/users`
- HTTP 方法映射：
  - `GET` - 获取资源
  - `POST` - 创建资源
  - `PUT` - 全量更新资源
  - `PATCH` - 部分更新资源
  - `DELETE` - 删除资源

#### 开发流程

1. **创建数据模型** (`app/models/`)
   ```python
   # app/models/example.py
   class ExampleModel(Base):
       __tablename__ = "examples"
       id = Column(Integer, primary_key=True)
       name = Column(String(100), nullable=False)
   ```

2. **定义数据模式** (`app/schemas/`)
   ```python
   # app/schemas/example.py
   class ExampleCreate(BaseModel):
       name: str
   
   class ExampleResponse(BaseModel):
       id: int
       name: str
   ```

3. **实现服务层** (`app/services/`)
   ```python
   # app/services/example.py
   async def create_example(db: Session, data: ExampleCreate):
       # 业务逻辑实现
   ```

4. **创建 API 路由** (`app/api/backend/`)
   ```python
   # app/api/backend/example.py
   @router.post("/", response_model=ExampleResponse)
   async def create_example(
       data: ExampleCreate,
       db: Session = Depends(get_db)
   ):
       return await example_service.create_example(db, data)
   ```

5. **注册路由** (`app/api/main.py`)
   ```python
   app.include_router(
       example_router,
       prefix="/api/v1/backend/examples",
       tags=["Examples"]
   )
   ```

### 权限控制

使用依赖注入实现权限控制：

```python
@router.get("/", dependencies=[Depends(check_permission('UserList'))])
async def get_users():
    # 需要 UserList 权限才能访问
```

### 数据库迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "添加新表"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 异步任务

```python
# 定义任务
@celery_app.task
def send_email(to: str, subject: str, body: str):
    # 任务实现
    pass

# 调用任务
send_email.delay("user@example.com", "主题", "内容")
```

### 代码质量

```bash
# 代码检查
./scripts/lint.sh

# 代码格式化
./scripts/format.sh

# 运行测试
./scripts/test.sh
```

### 代码生成

本项目提供代码生成工具，快速创建模板代码：

```bash
# 生成完整的 CRUD 代码
python app/gen/main.py -n user.UserModel -t all

# 仅生成 Schema
python app/gen/main.py -n user.UserModel -t schema
```

## 🌐 Nginx 配置

```nginx
server {
    listen 80;
    server_name api.example.com;
    root /path/to/fastapi/public;

    access_log /var/log/nginx/fastapi.access.log;
    error_log /var/log/nginx/fastapi.error.log;

    location / {
        if (!-e $request_filename) {
            proxy_pass http://127.0.0.1:8000/;
        }
        proxy_buffering off;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📚 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_user.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🚀 生产部署

### 环境变量配置

确保以下环境变量正确设置：

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=fastapi
MYSQL_PASSWORD=password
MYSQL_DB=fastapi

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 应用配置
SECRET_KEY=your-secret-key
DEBUG=false
```

### 性能优化

- 启用数据库连接池
- 配置 Redis 缓存
- 使用 Nginx 反向代理
- 启用 gzip 压缩
- 配置 CDN 加速静态资源

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发规范

- 遵循 PEP 8 代码风格
- 编写单元测试
- 更新相关文档
- 通过所有 CI 检查

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 [Issue](../../issues)

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL 工具包
- [Celery](https://docs.celeryq.dev/) - 分布式任务队列
- [Redis](https://redis.io/) - 内存数据结构存储

---

⭐ 如果这个项目对您有帮助，请给它一个 Star！
