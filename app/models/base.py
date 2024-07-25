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
    def from_dict(self, data: dict) -> None:
        '''将字典数据导入模型'''
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])


    def to_dict(self) -> dict:
        '''将模型转换为纯粹的字典'''
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


# 导入所有模型，以支持 alembic 自动追踪
from app.models import user, finance, cms, system_option, payment_settings, wechat
