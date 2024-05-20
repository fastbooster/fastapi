#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: celery_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 21:50


import os
from datetime import timedelta
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab

load_dotenv()
redis_url = f'redis://:{os.getenv("REDIS_PWD")}@{os.getenv('REDIS_HOST')
                                                 }:{os.getenv("REDIS_PORT")}/{os.getenv("REDIS_DB")}'

app = Celery('tasks', broker=redis_url, backend=redis_url)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    broker_connection_retry_on_startup=True,

    result_expires=3600,
    beat_schedule={
        'wechat_refresh_accesstoken': {
            'task': 'app.tasks.wechat.refresh_access_token',
            # 'schedule': timedelta(seconds=10),  # 每隔10秒执行一次
            'schedule': crontab(minute=0, hour="*/1"),  # 每隔1小时执行一次
            'args': ()
        },
    },
)
