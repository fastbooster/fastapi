#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 22:17

import json

from app.core.celery import app
from app.core.redis import get_redis
from app.core.log import logger
from app.core.wechat import wechat_manager
from app.constants.constants import REDIS_WECHAT


@app.task
def refresh_access_token():
    with get_redis() as redis:
        cache_data = redis.hgetall(REDIS_WECHAT)
        if cache_data is None:
            logger.info('系统没有添加任何微信媒体平台, 忽略刷新access_token')
            return

        for item in cache_data.items():
            config = json.loads(item[1])
            appid = config['appid']
            if config['status'] != 'enabled':
                logger.info(f'微信媒体平台({appid})已禁用, 忽略刷新access_token')
                return
            try:
                client = wechat_manager.get_instance(appid)
                client.fetch_access_token()
                logger.info(f'成功刷新微信媒体平台({appid})的access_token')
            except Exception as e:
                logger.error(f'刷新微信媒体平台({appid})的access_token失败: {e}')
