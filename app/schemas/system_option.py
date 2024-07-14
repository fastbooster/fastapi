#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:20

from datetime import datetime

from typing import List, Union, Optional

from pydantic import BaseModel, validator, Field

from app.schemas.schemas import PaginationParams


class OptionItem(BaseModel):
    id: Optional[int] = 0
    option_name: str
    option_value: Optional[str] = None
    richtext: Optional[int] = 0
    position: Optional[int] = 0
    autoload: Optional[int] = 0
    lock: Optional[int] = 0
    memo: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('richtext', 'autoload', 'lock')
    def validate_boolean_fields(cls, value):
        if value not in (0, 1):
            return 0
        return value

    @validator('position')
    def validate_position(cls, value):
        if value is not None and value < 0:
            return 0
        return value


class OptionListResponse(BaseModel):
    total: int
    items: List[OptionItem]


class OptionSearchQuery(PaginationParams):
    option_name: Optional[str] = None
    memo: Optional[str] = None
    locked: Optional[str] = Field(None, description="锁定状态：yes/no")
