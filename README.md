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
|-- public                  // Web根目录，用于提供静态文件访问
|-- docker                  // Docker镜像配置卷
|-- volumes                 // Docker容器数据卷
|-- scripts                 // 助手脚本目录
|-- restart.sh              // 容器重启脚本
```


### 本机开发

```shell
# 如果本机没有安装 mysql & redis, 可以通过 docker 启动服务来代替
docker compose -p <proj_name> -f docker-compose-dev.yml up -d

cp -r ./.env.example .env
cp -r ./config.example.yaml config.yaml
python -m venv .venv # 如果已经执行过，此步骤可跳过
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python start.py
```


### Docker部署

#### 由于服务器无法访问 Docker Hub，可以在本地导出所需镜像，再上传到服务器上使用

```shell
# 下载镜像
docker pull python:3.12-slim-bullseye
docker pull mysql:8.0.35
docker pull redis:7.2.1

# 导出镜像
docker image save python:3.12-slim-bullseye -o python.image
docker image save mysql:8.0.35 -o mysql.image
docker image save redis:7.2.1 -o redis.image

# 将镜像上传到服务器，导入镜像
docker image load -i python.image
docker image load -i mysql.image
docker image load -i redis.image
```

#### 选择不同的配置文件启动服务

```shell
# 创建 .env 和 config.yaml 并编辑配置信息
cp -r ./.env.example .env
cp -r ./config.example.yaml config.yaml

# 根据实际情况，选择不同的 docker-compose 文件启动服务
# docker-compose.yml 仅包含 server(fastapi), 其他服务在云端
# docker-compose-celery.yml 仅包含 celery, 其他服务在云端
# docker-compose-dev.yml 包含 mysql, redis, 其他服务如 fastapi, celery 在宿主机启动，方便调试
# docker-compose-full.yml 包含 server, celery, mysql, redis 单机容器部署
docker compose -p your_proj_name -f docker-compose.yml up -d --build

# 重建镜像
# 执行此命令后，如果有修改数据库配置，记得删除 volumes/mysql, redis 目录, 否者可能连接不上数据库
docker compose -p your_proj_name down

# 如果不删除 volumes/mysql, redis，则需更改目录用户为当前用户，否者容器无法写入 volumes 目录，导致启动失败
chown -R user:user volumes

# 也可通过重启脚本重新构建镜像
./restart.sh docker-compose.yml
./restart.sh docker-compose-celery.yml
./restart.sh docker-compose-dev.yml
./restart.sh docker-compose-full.yml
```

#### 进入容器，手动迁移数据库 （TODO：启动容器时自动执行）和初始化必要数据

```shell
docker exec -it your_proj_name-server-1 bash
# 详见下面的 1. 数据库迁移指南, 2. 初始化必要数据
```


### Nginx

```
server {
    listen 80;
    server_name api.intranet.com;
    root /path/to/fastapi/public;

    access_log /var/log/nginx/proj_name.access.log;
    error_log /var/log/nginx/proj_name.error.log;

    location / {
        if (!-e $request_filename) {
            proxy_pass http://127.0.0.1:<PORT>/;
        }
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
alembic downgrade base # 重置数据库
alembic downgrade version_id # 回滚到指定版本

# 5. 查看帮助
alembic --help
```


### 初始化必要数据

TODO: 编写统一交互式初始化脚本

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

# 5. 初始化支付渠道
python app/utils/init_payment_channel.py
```


### 接口开发指南

#### 约定

1. 接口使用 `RESTful API` 风格开发，通过 `HTTP Method` 实现资源访问和管理，API端点命名统一采用 `复数名词`，如：`/api/v1/backend/users`

2. 前端调用接口时，空值字段请勿传入，后端将自动处理为 `None`，例如：`status=''` 时就不要提交此字段

| HTTP动词  | 是否幂等  | 约定用法
|----------|----------|-------------
| head     | 是       | 无
| options  | 是       | 无
| post     | 否       | 创建资源
| get      | 是       | 获取资源
| put      | 是       | 全量更新资源
| patch    | 否       | 部分更新数据
| delete   | 是       | 删除资源

#### 流程

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
    # 前台启动单worker异步任务（专门用于积分余额动账）
    celery -A app.celery_single_worker worker --loglevel=info

    # 前台启动异步任务（先启动）
    celery -A app.celery_worker worker --loglevel=info

    # 前台启动定时任务（后启动，定时任务的本质是生成异步任务，所以必须先启动异步任务）
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
4. [wechatpy](https://www.wechatpy.org/) 微信公众号 Python SDK
5. [Python Alipay SDK](https://github.com/fzlee/alipay/blob/master/docs/apis.zh-hans.md) with SHA1/SHA256 support
6. [RESTful API 接口规范详解](https://cloud.tencent.com/developer/article/2360813)
7. [RESTful API 设计最佳实践](https://segmentfault.com/a/1190000011516151)
