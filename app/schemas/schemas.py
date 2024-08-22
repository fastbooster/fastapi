#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: schemas.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/19 10:06

from enum import Enum
from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class StatusType(Enum):
    """状态类型"""
    ENABLED = 'enabled'
    DISABLED = 'disabled'


class MysqlBoolType(Enum):
    """自定义 mysql 布尔类型，使用字符串替代 0/1"""
    YES = 'yes'
    NO = 'no'


class ClientType(Enum):
    """自定义客户端类型"""
    PC_BROWSER = 'pc_browser'
    MOBILE_BROWSER = 'mobile_browser'
    WECHAT_BROWSER = 'wechat_browser'
    ALIPAY_BROWSER = 'alipay_browser'
    ANDROID_APP = 'android_app'
    IOS_APP = 'ios_app'


class PaginationParams(BaseModel):
    page: Optional[int] = Query(1, ge=1, description="页码")
    size: Optional[int] = Query(10, ge=1, le=100, description="每页条数")
    export: Optional[int] = Query(0, ge=0, le=1, description="是否导出数据")


class ResponseSuccess(BaseModel):
    status: Optional[str] = 'OK'
