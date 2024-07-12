#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/11 10:30

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.payment_channel import PaymentChannelOutItem, PaymentChannelItem
from app.schemas.payment_config import PaymentConfigOutItem, PaymentConfigSafeItem


class PaymentSettingItem(BaseModel):
    '''支付设置，模型全量数据'''
    channel: PaymentChannelItem
    children: Optional[List[PaymentConfigSafeItem]]


class PaymentSettingListResponse(BaseModel):
    '''支付设置列表，模型全量数据'''
    total: int
    items: List[PaymentSettingItem]


class PaymentSettingOutItem(BaseModel):
    '''支付设置，精简数据'''
    channel: PaymentChannelOutItem
    children: Optional[List[PaymentConfigOutItem]]


class PaymentSettingOutListResponse(BaseModel):
    '''支付设置列表，精简数据'''
    total: int
    items: List[PaymentSettingOutItem]


class PaymentSettingsSortForm(BaseModel):
    '''前端排好序，将 id 按顺序传给后端保存'''
    channel_ids: List[int]
    config_ids: List[int]
