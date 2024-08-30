#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File: cache.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/8/30 16:53

from typing import List, Optional, Any

from pydantic import BaseModel, Field


class CacheItem(BaseModel):
    """Cache数据模型"""
    title: str = Field(description="标题")
    key: str = Field(description="缓存键")
    type: str = Field(description="缓存类型")
    count: Optional[int] = Field(0, description="缓存数量")


class CacheListResponse(BaseModel):
    """列表响应数据模型"""
    total: int
    items: List[CacheItem]


class CacheDetailResponse(BaseModel):
    """详情响应数据模型"""
    total: int
    items: Any
