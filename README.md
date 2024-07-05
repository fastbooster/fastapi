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
|   |-- constants           // 常量目录
|   |-- core                // 核心组件目录
|   |-- models              // 模型目录 (SQLAlchemy ORM)
|   |-- schemas             // 表单目录 (pydantic schemas)
|   |-- services            // 服务类 (CRUD+)
|   |-- tasks               // 异步任务 (Celery)
|   |-- utils               // 助手工具
|-- docker                  // Docker镜像配置卷
|-- volumes                 // Docker容器数据卷
|-- scripts                 // 助手脚本目录
```


### 本机开发

```shell
# 如果本机没有安装 mysql & redis, 可以通过 docker 启动服务来代替
docker compose -p <proj_name> -f docker-compose-dev.yml up -d --build

cp -r ./.env.example .env
cp -r ./config.example.yaml config.yaml
python -m venv .venv # 如果已经执行过，此步骤可跳过
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python start.py
```


### Docker部署

```shell
cp -r ./.env.example .env
docker compose -p <proj_name> down # 执行此命令后，如果有修改数据库配置，记得删除 volumes/mysql/* 目录, 否者可能连接不上数据库
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

# 2. 初始化角色
python app/utils/init_role.py

# 3. 初始化用户
python app/utils/init_user.py

# 4. 初始化城市
python app/utils/init_city.py
```


### 接口开发指南

1. 创建接口路由文件，如：`./app/api/backend/user.py`

2. 将其加入到包，以方便导入，如：`./app/api/backend/__init__.py`

3. 将路由加入到路由组 `./app/api/main.py` 并定义前缀和文档 `tags`

4. 后台路由菜单级鉴权，添加依赖注入即可，如：`dependencies=[Depends(check_permission('UserList'))]`
   这里的 `UserList` 是权限菜单定义的前端组件名称，详见: `./app/utils/init_permissions.py`

    参考文档：[Dependencies in path operation decorators](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/)

5. 语法检查并修复错误

   ```shell
   # 进入虚拟环境
   source .venv/bin/activate
   
   # 语法检查
   ./scripts/lint.sh
   ```


### 异步任务

1. 开发测试

    ```shell
    # 前台启动单worker异步任务(专门用于积分余额动账)
    celery -A app.celery_single_worker worker --loglevel=info

    # 前台启动异步任务
    celery -A app.celery_worker worker --loglevel=info

    # 前台启动定时任务
    celery -A app.celery_worker beat -s --loglevel=info

    # 停止 celery 任务
    ./stop_celery.sh
    ```

2. 生产部署
   
   ```shell
   ./start_celery.sh
   ```

### 参考文档列表

1. [FastAPI](https://fastapi.tiangolo.com/)
2. [RedisPy](https://redis.io/docs/latest/develop/connect/clients/python/)
3. [Celery](https://docs.celeryq.dev/en/stable/index.html)
4. [Restful API 接口规范详解](https://cloud.tencent.com/developer/article/2360813)
5. [wechatpy](https://www.wechatpy.org/) 微信公众号 Python SDK
