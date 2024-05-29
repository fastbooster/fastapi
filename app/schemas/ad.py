#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ad.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/29 17:03

from typing import Optional

from pydantic import BaseModel, validator
from enum import Enum

from app.schemas.schemas import PaginationParams


class PositionType(Enum):
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'


class SpaceSearchQuery(PaginationParams):
    id: Optional[int] = 0
    name: Optional[str] = None
    status: Optional[int] = -1


class SpaceAddForm(BaseModel):
    name: str
    width: Optional[int] = 1920
    height: Optional[int] = 600
    status: Optional[int] = 1

    @validator('status')
    def validate_boolean_fields(cls, value):
        if value not in (0, 1):
            return 0
        return value


class SpaceEditForm(SpaceAddForm):
    id: int


class AdSearchQuery(PaginationParams):
    id: Optional[int] = 0
    space_id: Optional[int] = 0
    status: Optional[int] = -1


class AdAddForm(BaseModel):
    space_id: int
    position: PositionType
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    pc_cover: Optional[str] = None
    mobile_cover: Optional[str] = None
    button_title: Optional[str] = None
    button_url: Optional[str] = None
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

    @validator('space_id')
    def validate_space_id(cls, value):
        if value < 1:
            raise ValueError('请选择正确广告位')
        return value


class AdEditForm(AdAddForm):
    id: int
