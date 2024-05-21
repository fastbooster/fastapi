#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 10:05

from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.schemas import PaginationParams


class PostSearchQuery(PaginationParams):
    id: Optional[int] = 0
    pid: Optional[int] = -1
    category_id: Optional[int] = -1
    user_id: Optional[int] = -1
    title: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[int] = -1


class PostAddForm(BaseModel):
    pid: Optional[int] = 0
    category_id: Optional[int] = 0
    user_id: Optional[int] = 0
    title: str
    subtitle: Optional[str] = None
    keywords: Optional[str] = None
    digest: Optional[str] = None
    content: str
    author: Optional[str] = None
    editor: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    hero_image_url: Optional[str] = None
    price: Optional[float] = 0.0000
    price_point: Optional[int] = 0
    view_num: Optional[int] = 0
    like_num: Optional[int] = 0
    collect_num: Optional[int] = 0
    comment_num: Optional[int] = 0
    comment_status: Optional[int] = 1
    status: Optional[int] = 1

    @validator('status', 'comment_status')
    def validate_boolean_fields(cls, value):
        if value not in (0, 1):
            return 0
        return value


class PostEditForm(PostAddForm):
    id: int
