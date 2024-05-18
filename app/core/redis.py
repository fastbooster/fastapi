#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: redis.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os
import redis

from contextlib import contextmanager

# https://redis.io/docs/latest/develop/connect/clients/python/
REDIS_CONFIG = {
    'host': os.getenv("REDIS_HOST"),
    'port': int(os.getenv("REDIS_PORT")),
    'password': os.getenv("REDIS_PWD"),
    'db': int(os.getenv("REDIS_DB")),
    'max_connections': int(os.getenv("REDIS_POOL_SIZE")),
    'decode_responses': True
}
pool = redis.ConnectionPool(**REDIS_CONFIG)


@contextmanager
def get_redis():
    r = redis.Redis(connection_pool=pool)
    yield r
