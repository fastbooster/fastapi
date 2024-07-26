#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/25 22:25

import json

from wechatpy import WeChatClient
from wechatpy.session.redisstorage import RedisStorage

from app.core.redis import get_redis
from app.constants.constants import REDIS_WECHAT


class WechatManager:
    '''单进程单例模式的微信客户端实例，不使用多进程以降低资源消耗'''
    _instances = {}

    def get_instance(self, appid: str = None) -> WeChatClient:
        if appid in self._instances:
            return self._instances[appid]
        try:
            with get_redis() as redis:
                wechat_config = json.loads(redis.hget(REDIS_WECHAT, appid))
                if not wechat_config:
                    raise Exception(f'微信媒体平台(appid={appid})不存在，请先添加配置')
                session_interface = RedisStorage(
                    redis, prefix='wechatpy')
                self._instances[appid] = WeChatClient(
                    wechat_config['appid'], wechat_config['appsecret'], session=session_interface)
                return self._instances[appid]
        except Exception as e:
            raise e


wechat_manager = WechatManager()
