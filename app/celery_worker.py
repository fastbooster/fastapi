#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: celery_worker.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 23:42

from app.core.celery import app

if __name__ == '__main__':
    app.start()
