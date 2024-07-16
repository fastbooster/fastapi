#!/bin/bash

# 使用范例
# ./restart.sh docker-compose.yml
# ./restart.sh docker-compose-dev.yml
# ./restart.sh docker-compose-full.yml

if [ ! -f "$1" ]; then
    echo "Docker Compose 配置文件 '$1' 不存在"
    exit
fi

docker compose -p fastapi down
docker rmi fastapi-server
docker rmi fastapi-celery
docker compose -p fastapi -f $1 up -d --build
docker ps

echo "--------------------------------------------------------------"
echo "恭喜, 重启完成，如果是首次启动，请进入容器初始化必要数据，详见 README.md"
echo "--------------------------------------------------------------"

docker logs -f fastapi-server-1
