#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: banner.py
# Author: FastBooster Generator
# Time: 2024-08-23 19:52

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, PaginationParams


class PositionType(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    TOP = 'top'
    BOTTOM = 'bottom'


class BannerBase(BaseModel):
    """基础数据模型"""
    adspace_id: Optional[int] = Field(None, description='广告位ID')
    position: Optional[PositionType] = Field(None, description='位置:left|right|center|top|bottom')
    title: Optional[str] = Field(None, description='标题')
    subtitle: Optional[str] = Field(None, description='子标题')
    description: Optional[str] = Field(None, description='描述')
    content: Optional[str] = Field(None, description='详细内容')
    pc_cover: Optional[str] = Field(None, description='PC端封面图')
    mobile_cover: Optional[str] = Field(None, description='移动端封面图')
    button_title: Optional[str] = Field(None, description='按钮标题')
    button_url: Optional[str] = Field(None, description='按钮地址')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')
    asc_sort_order: Optional[int] = Field(None, description='排序')


class BannerForm(BannerBase):
    """表单数据模型"""
    pass


class BannerItem(BannerBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class BannerPublicItem(BaseModel):
    """公开数据模型"""
    pass


class BannerListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[BannerItem]


class BannerPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[BannerPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    id: Optional[int] = None
    space_id: Optional[int] = None
    status: Optional[StatusType] = None
