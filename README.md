# FastAPI 接口服务器


### 目录结构

```shell
.                           // 根目录
|-- app                     // 应用目录
|   |-- alembic             // 数据库迁移工具
|   |-- api                 // API目录
|   |-- |-- routes          // 通用路由
|   |-- |-- frontend        // 前端路由
|   |-- |-- backend         // 后端路由
|   |-- core                // 核心组件目录
|   |-- services            // 服务类 (CRUD+)
|   |-- schemas             // 表单目录 (pydantic schemas)
|   |-- models              // 模型目录 (SQLAlchemy ORM)
|   |-- utils               // 助手工具
|   ...                     // 待完善...
```


### 本机开发

```shell
cp -r ./.env.example .env
pip install --upgrade pip
pip install -r requirements.txt
python start.py
```


### Docker部署

```shell
cp -r ./.env.example .env
docker compose -p <proj_name> down
docker compose -p <proj_name> -f docker-compose.yml up -d --build
```


### Nginx

```
server {
    listen 80;
    server_name api.intranet.com;
    root /usr/share/nginx/html;

    access_log /var/log/nginx/proj_name.access.log;
    error_log /var/log/nginx/proj_name.error.log;

    location / {
        proxy_pass http://127.0.0.1:<PORT>/;
        proxy_buffering off;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```


### 数据库迁移指南

```shell
# 1. 在 ./app/models 目录下创建模型文件，并将其导入到 ./app/models/base.py

# 2. 生成迁移脚本
alembic revision --autogenerate -m "message"

# 3. 执行迁移脚本
alembic upgrade head

# 4. 回滚迁移脚本
alembic downgrade version_id

# 5. 查看帮助
alembic --help
```


### 初始化必要数据

```shell
# 1. 初始化权限菜单
# 更新权限菜单后可反复执行此命令
python app/utils/init_permissions.py

# 2. 初始化用户
python app/utils/init_user.py
```
