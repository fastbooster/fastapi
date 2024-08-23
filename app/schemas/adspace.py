#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: adspace.py
# Author: FastBooster Generator
# Time: 2024-08-23 18:45

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, PaginationParams


class AdspaceBase(BaseModel):
    """基础数据模型"""
    name: Optional[str] = Field(None, description='广告名称')
    width: Optional[int] = Field(None, description='推荐宽度')
    height: Optional[int] = Field(None, description='推荐高度')
    status: Optional[StatusType] = Field(StatusType.ENABLED.value, description='状态: enabled/disabled')


class AdspaceForm(AdspaceBase):
    """表单数据模型"""
    pass


class AdspaceItem(AdspaceBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class AdspacePublicItem(BaseModel):
    """公开数据模型"""
    pass


class AdspaceListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[AdspaceItem]


class AdspacePublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[AdspacePublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    id: Optional[int] = 0
    name: Optional[str] = None
    status: Optional[StatusType] = StatusType.ENABLED.value
