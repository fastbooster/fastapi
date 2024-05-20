#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 16:56

from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.schemas import PaginationParams


class CategorySearchQuery(PaginationParams):
    id: Optional[int] = 0
    name: Optional[str] = None
    alias: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[int] = -1


class CategoryAddForm(BaseModel):
    name: str
    alias: str
    keywords: Optional[str] = None
    asc_sort_order: Optional[int] = 0
    status: Optional[int] = 1

    @validator('status')
    def validate_boolean_fields(cls, value):
        if value not in (0, 1):
            return 0
        return value

    @validator('asc_sort_order')
    def validate_position(cls, value):
        if value is not None and value < 0:
            return 0
        return value


class CategoryEditForm(CategoryAddForm):
    id: int
