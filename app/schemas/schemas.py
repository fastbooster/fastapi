#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: schemas.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/19 10:06

from typing import Optional

from fastapi import Query
from pydantic import BaseModel
from enum import Enum


class StatusType(Enum):
    ENABLED = 'enabled'
    DISABLED = 'disabled'


class MysqlBoolType(Enum):
    YES = 'yes'
    NO = 'no'


class PaginationParams(BaseModel):
    page: Optional[int] = Query(1, ge=1, description="页码")
    size: Optional[int] = Query(10, ge=1, le=100, description="每页条数")
    export: Optional[int] = Query(0, ge=0, le=1, description="是否导出数据")


class ResponseSuccess(BaseModel):
    status: Optional[str] = 'OK'
