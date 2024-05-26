#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: celery_single_worker.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/24 17:25

from app.core.single_celery import app_single

if __name__ == '__main__':
    app_single.start()
