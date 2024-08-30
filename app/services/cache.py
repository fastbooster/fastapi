#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File: cache.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/8/30 17:40

from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD, REDIS_PAYMENT_CHANNEL, REDIS_PAYMENT_CONFIG, \
    REDIS_WECHAT, REDIS_POST_CATEGORY
from app.core.redis import get_redis
from app.services import system_option, payment_channel, payment_config, wechat, post_category


def lists() -> dict:
    items = [
        {
            'title': '系统选项',
            'type': 'hash',
            'key': REDIS_SYSTEM_OPTIONS_AUTOLOAD,
        },
        {
            'title': '支付渠道',
            'type': 'hash',
            'key': REDIS_PAYMENT_CHANNEL,
        },
        {
            'title': '支付配置',
            'type': 'hash',
            'key': REDIS_PAYMENT_CONFIG,
        },
        {
            'title': '微信媒体平台',
            'type': 'hash',
            'key': REDIS_WECHAT,
        },
        {
            'title': '文章分类',
            'type': 'hash',
            'key': REDIS_POST_CATEGORY,
        },
    ]
    with get_redis() as redis:
        for item in items:
            if item['type'] == 'hash':
                item['count'] = redis.hlen(item['key'])
        return {"total": len(items), "items": items}


def detail(key: str):
    with get_redis() as redis:
        if not redis.exists(key):
            raise KeyError(f'缓存 {key} 不存在')
        cache_type = redis.type(key)
        match cache_type:
            case 'hash':
                return {"total": redis.hlen(key), "items": redis.hgetall(key)}
            case 'list':
                return {"total": redis.llen(key), "items": redis.lrange(key, 0, -1)}
            case 'set':
                return {"total": redis.scard(key), "items": redis.smembers(key)}
            case 'zset':
                return {"total": redis.zcard(key), "items": redis.zrange(key, 0, -1)}
            case 'string':
                return {"total": 1, "items": [redis.get(key)]}
            case _:
                raise KeyError(f'缓存 {key} 不存在')


def rebuild_cache(key: str):
    with get_redis() as redis:
        if not redis.exists(key):
            raise KeyError(f'缓存 {key} 不存在')
        if REDIS_SYSTEM_OPTIONS_AUTOLOAD == key:
            system_option.rebuild_cache()
        elif REDIS_PAYMENT_CHANNEL == key:
            payment_channel.rebuild_cache()
        elif REDIS_PAYMENT_CONFIG == key:
            payment_config.rebuild_cache()
        elif REDIS_WECHAT == key:
            wechat.rebuild_cache()
        elif REDIS_POST_CATEGORY == key:
            post_category.rebuild_cache()
        else:
            raise KeyError(f'赞不支持缓存 {key} 重建')
