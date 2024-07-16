#!/bin/sh

# 使用独立容器运行 Celery, 详见 Dockerfile.celery
celery -A app.celery_single_worker worker --loglevel=info &
celery -A app.celery_worker worker --loglevel=info &
celery -A app.celery_worker beat -s --loglevel=info &
