#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: base.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/16 11:18

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseMixin:
    """基础数据库模型"""

    def from_dict(self, data: dict) -> None:
        """将字典数据导入模型"""
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])

    def to_dict(self) -> dict:
        """将模型转换为纯粹的字典"""
        if hasattr(self, '__table__'):
            result = {}
            for c in self.__table__.columns:
                value = getattr(self, c.key)
                # 解决问题: TypeError: Object of type datetime is not JSON serializable
                if value is not None and hasattr(value, 'isoformat'):
                    value = value.isoformat()
                result[c.key] = value
            return result
        return {}


# 导入所有模型，以支持 alembic 自动追踪
from app.models import user, finance, cms, system_option, payment_settings, wechat
