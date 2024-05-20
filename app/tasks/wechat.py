#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 22:17

from celery import shared_task


@shared_task
def refresh_access_token():
    pass
