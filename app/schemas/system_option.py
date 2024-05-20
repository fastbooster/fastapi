#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:20

from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.schemas import PaginationParams


class OptionSearchQuery(PaginationParams):
    option_name: Optional[str] = None
    memo: Optional[str] = None


class OptionAddForm(BaseModel):
    option_name: str
    option_value: str
    richtext: Optional[int] = 0
    position: Optional[int] = 0
    autoload: Optional[int] = 0
    lock: Optional[int] = 0
    memo: Optional[str] = None

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


class OptionEditForm(OptionAddForm):
    id: int
