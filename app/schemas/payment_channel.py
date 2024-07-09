#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 10:38

from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas.schemas import StatusType, MysqlBoolType, PaginationParams


class PaymentChannelItem(BaseModel):
    id: Optional[int] = 0
    key: str
    name: str
    icon: Optional[str] = None
    locked: Optional[MysqlBoolType] = MysqlBoolType.NO.value
    asc_sort_order: Optional[int] = None
    status: Optional[StatusType] = StatusType.ENABLED.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaymentChannelListResponse(BaseModel):
    total: int
    items: List[PaymentChannelItem]


class PaymentChannelSearchQuery(PaginationParams):
    key: Optional[str] = None
    name: Optional[str] = None
    status: Optional[StatusType] = StatusType.ENABLED.value
