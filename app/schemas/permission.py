#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permission.py
# Author: FastBooster Generator
# Time: 2024-08-22 12:22

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import PaginationParams


class PermissionBase(BaseModel):
    """基础数据模型"""
    pid: Optional[int] = Field(None, description='上级ID')
    name: Optional[str] = Field(None, description='名称')
    icon: Optional[str] = Field(None, description='图标')
    component_name: Optional[str] = Field(None, description='路由组件名称')
    asc_sort_order: Optional[int] = Field(None, description='排序')


class PermissionForm(PermissionBase):
    """表单数据模型"""
    pass


class PermissionItem(PermissionBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(None, description="创建时间")
    updated_at: datetime = Field(None, description="更新时间")


class PermissionPublicItem(BaseModel):
    """公开数据模型"""
    pass


class PermissionNestedItem(PermissionItem):
    """嵌套模型"""
    children: Optional[List[PermissionItem]] = None


class PermissionNestResponse(BaseModel):
    """嵌套响应模型"""
    total: int
    items: List[PermissionNestedItem]


class PermissionListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[PermissionItem]


class PermissionPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[PermissionPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    pass
