#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: FastBooster Generator
# Time: 2024-08-22 15:32

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, PaginationParams


class PostCategoryBase(BaseModel):
    """基础数据模型"""
    name: Optional[str] = Field(None, description='名称')
    alias: Optional[str] = Field(None, description='URL别名')
    keywords: Optional[str] = Field(None, description='关键字')
    asc_sort_order: Optional[int] = Field(None, description='排序')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')


class PostCategoryForm(PostCategoryBase):
    """表单数据模型"""
    pass


class PostCategoryItem(PostCategoryBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class PostCategoryPublicItem(PostCategoryBase):
    """公开数据模型"""
    pass


class PostCategoryListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[PostCategoryItem]


class PostCategoryPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[PostCategoryPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    name: Optional[str] = Field(None, description='名称')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')
