#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: base.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/16 11:18

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin:
    '''基础混入类，提供一些通用方法'''
    def from_dict(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])


# 导入所有模型，以支持 alembic 自动追踪
from app.models import user, finance, cms, system_option, payment_settings
