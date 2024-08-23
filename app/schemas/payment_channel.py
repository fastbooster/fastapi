#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: FastBooster Generator
# Time: 2024-08-23 12:11

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, MysqlBoolType, PaginationParams


class PaymentChannelBase(BaseModel):
    """基础数据模型"""
    key: Optional[str] = Field(None, description='键名')
    name: Optional[str] = Field(None, description='名称')
    icon: Optional[str] = Field(None, description='图标')
    locked: Optional[MysqlBoolType] = Field(MysqlBoolType.NO.value, description='锁定: yes/no')
    asc_sort_order: Optional[int] = Field(None, description='排序')
    status: Optional[StatusType] = Field(StatusType.ENABLED.value, description='状态: enabled/disabled')


class PaymentChannelForm(PaymentChannelBase):
    """表单数据模型"""
    pass


class PaymentChannelItem(PaymentChannelBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class PaymentChannelPublicItem(BaseModel):
    """公开数据模型"""
    key: str
    name: str


class PaymentChannelListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[PaymentChannelItem]


class PaymentChannelPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[PaymentChannelPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    key: Optional[str] = None
    name: Optional[str] = None
    status: Optional[StatusType] = None
