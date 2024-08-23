#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ${file_name}
# Author: FastBooster Generator
# Time: ${create_time}

from datetime import datetime
from enum import Enum
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, MysqlBoolType, PaginationParams


class ${model}Base(BaseModel):
    """基础数据模型"""
% for column in columns:
    ${column['name']}: Optional[${column['type']}] = Field(None, description='${column["comment"]}')
% endfor


class ${model}Form(${model}Base):
    """表单数据模型"""
    pass


class ${model}Item(${model}Base):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class ${model}PublicItem(BaseModel):
    """公开数据模型"""
    pass


class ${model}ListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[${model}Item]


class ${model}PublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[${model}PublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    pass
