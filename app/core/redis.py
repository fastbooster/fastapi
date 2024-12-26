#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: redis.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os
from contextlib import contextmanager

import redis
from dotenv import load_dotenv
from redis import Connection

# 必须单独导入，否则在 Celery 的 tasks 中无法正确获取配置
load_dotenv()

redis_port_env = os.getenv("REDIS_PORT")
redis_db_env = os.getenv("REDIS_DB")
redis_pull_size_env = os.getenv("REDIS_POOL_SIZE")
max_connections = int(redis_pull_size_env) if redis_pull_size_env else 5

# https://redis.io/docs/latest/develop/connect/clients/python/
REDIS_CONFIG = {'host': os.getenv("REDIS_HOST"), 'port': int(redis_port_env) if redis_port_env else 6379,
    'password': os.getenv("REDIS_PWD"), 'db': int(redis_db_env) if redis_db_env else 0, 'decode_responses': True}
pool = redis.ConnectionPool(Connection, max_connections, **REDIS_CONFIG)


@contextmanager
def get_redis():
    r = redis.Redis(connection_pool=pool)
    yield r


def get_redis_url(db_index: int = -1) -> str:
    usr = os.getenv("REDIS_USR")
    pwd = os.getenv("REDIS_PWD")
    if '@' in pwd:
        raise ValueError("Redis 密码不能包含 '@' 字符")
    if db_index == -1:
        db_index = os.getenv("REDIS_DB") if os.getenv("REDIS_DB") else 0
    redis_url = f'redis://{usr}:{pwd}@{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{db_index}'
    return redis_url
