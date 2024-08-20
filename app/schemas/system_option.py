#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:20

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import PaginationParams


class SystemOptionBase(BaseModel):
    """基础数据模型"""
    option_name: str = Field(pattern=r"^[a-zA-Z0-9-_]{1,50}$", description="选项名称")
    option_value: Optional[str] = Field(None, description="选项值")
    richtext: Optional[int] = Field(0, ge=0, le=1, description="是否为富文本")
    position: Optional[int] = Field(0, description="位置")
    autoload: Optional[int] = Field(0, ge=0, le=1, description="是否自动加载")
    lock: Optional[int] = Field(0, ge=0, le=1, description="是否锁定")
    public: Optional[int] = Field(0, ge=0, le=1, description="是否公开")
    memo: Optional[str] = Field(None, description="备注")


class SystemOptionForm(SystemOptionBase):
    """表单数据模型"""
    pass


class SystemOptionItem(SystemOptionBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(None, description="创建时间")
    updated_at: datetime = Field(None, description="更新时间")


class SystemOptionResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[SystemOptionItem]


class SystemOptionPublicItem(BaseModel):
    """公开数据模型"""
    option_name: str = Field(description='选项名称')
    option_value: str = Field(description='选项值')


class SystemOptionPublicResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[SystemOptionPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    option_name: Optional[str] = Field(None, description="选项名称")
    memo: Optional[str] = Field(None, description="备注")
    locked: Optional[int] = Field(None, ge=0, le=1, description="锁定状态")
    public: Optional[int] = Field(None, ge=0, le=1, description="是否公开")
