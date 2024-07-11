#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/11 10:30

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.payment_channel import PaymentChannelItem
from app.schemas.payment_config import PaymentConfigSafeItem


class PaymentSettingItem(BaseModel):
    channel: PaymentChannelItem
    children: Optional[List[PaymentConfigSafeItem]]


class PaymentSettingListResponse(BaseModel):
    total: int
    items: List[PaymentSettingItem]


class PaymentSettingsSortForm(BaseModel):
    '''前端排好序，将 id 按顺序传给后端保存'''
    channel_ids: List[int]
    config_ids: List[int]
