#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 22:17

from celery import shared_task

from app.core.celery import app
from app.core.log import logger


@app.task
def refresh_access_token():
    pass
