#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post.py
# Author: FastBooster Generator
# Time: 2024-08-22 14:09

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, PaginationParams


class PostBase(BaseModel):
    """基础数据模型"""
    pid: Optional[int] = Field(None, description='上级ID')
    category_id: Optional[int] = Field(None, description='分类ID')
    user_id: Optional[int] = Field(None, description='用户ID')
    title: Optional[str] = Field(None, description='标题')
    subtitle: Optional[str] = Field(None, description='副标题')
    keywords: Optional[str] = Field(None, description='关键字')
    digest: Optional[str] = Field(None, description='摘要')
    content: Optional[str] = Field(None, description='内容')
    author: Optional[str] = Field(None, description='作者')
    editor: Optional[str] = Field(None, description='责编')
    source: Optional[str] = Field(None, description='来源')
    source_url: Optional[str] = Field(None, description='来源URL')
    hero_image_url: Optional[str] = Field(None, description='首图')
    price: Optional[Decimal] = Field(None, description='价格')
    price_point: Optional[int] = Field(None, description='积分价格')
    view_num: Optional[int] = Field(None, description='浏览量')
    like_num: Optional[int] = Field(None, description='点赞量')
    collect_num: Optional[int] = Field(None, description='收藏量')
    comment_num: Optional[int] = Field(None, description='评论量')
    comment_status: Optional[StatusType] = Field(None, description='评论状态: enabled/disabled')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')


class PostForm(PostBase):
    """表单数据模型"""
    pass


class PostItem(PostBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class PostPublicItem(BaseModel):
    """公开数据模型"""
    pass


class PostListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[PostItem]


class PostPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[PostPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    id: Optional[int] = None
    pid: Optional[int] = None
    category_id: Optional[int] = None
    user_id: Optional[int] = None
    title: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[StatusType] = None
