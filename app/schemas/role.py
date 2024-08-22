#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: FastBooster Generator
# Time: 2024-08-22 13:26

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import PaginationParams


class RoleBase(BaseModel):
    """基础数据模型"""
    name: Optional[str] = Field(None, description='角色名称')
    permissions: Optional[str] = Field('[]', description='权限列表')


class RoleForm(RoleBase):
    """表单数据模型"""
    pass


class RoleItem(RoleBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(None, description="创建时间")
    updated_at: datetime = Field(None, description="更新时间")


class RolePublicItem(BaseModel):
    """公开数据模型"""
    pass


class RoleListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[RoleItem]


class RolePublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[RolePublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    name: Optional[str] = None
