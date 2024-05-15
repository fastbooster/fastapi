# FastAPI 接口服务器


### Local

```shell
cp -r ./.env.example .env
pip install --upgrade pip
pip install -r requirements.txt
python start.py
```

### Docker

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
