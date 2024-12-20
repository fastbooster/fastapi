#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: single_celery.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/24 16:36

import os
from dotenv import load_dotenv
from celery import Celery
from app.core.redis import get_redis_url

load_dotenv()
db_index = int(os.getenv('REDIS_DB_FINANCE')) if os.getenv(
    'REDIS_DB_FINANCE') else 1
redis_url = get_redis_url(db_index=db_index)
app_single = Celery('single_worker', broker=redis_url, backend=redis_url)

app_single.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_default_queue='single_worker_queue',
    worker_concurrency=1,
    include=['app.tasks.finance'],
)
