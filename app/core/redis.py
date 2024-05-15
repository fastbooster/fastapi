#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: redis.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os

import redis

redis_client = redis.Redis(
    os.getenv("REDIS_SERVER"), os.getenv("REDIS_PORT"), os.getenv("REDIS_DB"),
    password=os.getenv("REDIS_PWD"),
    decode_responses=True)
redis_client.ping()
