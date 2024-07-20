#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/18 21:44

from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.schemas import PaginationParams
from app.schemas.finance import PaymentStatusType, PaymentChannelType


class BalanceRechargeItem(BaseModel):
    '''全量模型字段'''
    id: Optional[int] = 0
    user_id: Optional[int] = 0
    trade_no: Optional[str] = Field(max_length=32, description="交易号")

    amount: Optional[float] = Field(0, description="充值数量")
    price: Optional[float] = Field(0, description="支付金额")
    gift_amount: Optional[float] = Field(0, description="赠送数量")
    refund_amount: Optional[float] = Field(0, description="退款数量")
    refund_gift_amount: Optional[float] = Field(0, description="退款赠送数量")

    payment_status: Optional[PaymentStatusType] = Field(
        PaymentStatusType.CREATED.value, description="付款状态")
    payment_channel: Optional[PaymentChannelType] = Field(
        PaymentChannelType.WECHATPAY.value, description="支付渠道")
    payment_appid: Optional[str] = Field(None, description="支付APPID")
    payment_time: Optional[datetime] = Field(None, description="付款时间")
    payment_response: Optional[str] = Field(None, description="支付结果")
    refund_response: Optional[str] = Field(None, description="退款结果")

    audit_user_id: Optional[int] = Field(0, description="审核人员ID")
    audit_user_name: Optional[str] = Field(None, description="审核人员姓名")
    audit_reply: Optional[str] = Field(None, description="审核回复")
    audit_time: Optional[datetime] = Field(None, description="审核时间")
    audit_ip: Optional[str] = Field(None, description="审核人员IP地址")

    user_ip: Optional[str] = Field(None, description="用户充值时的IP地址")
    auto_memo: Optional[str] = Field(None, description="自动备注")
    back_memo: Optional[str] = Field(None, description="后台备注")

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BalanceRechargeOutItem(BaseModel):
    '''对外模型字段'''
    trade_no: Optional[str] = Field(max_length=32, description="交易号")
    amount: Optional[float] = Field(0, description="充值数量")
    price: Optional[float] = Field(0, description="支付金额")
    gift_amount: Optional[float] = Field(0, description="赠送数量")
    refund_amount: Optional[float] = Field(0, description="退款数量")
    refund_gift_amount: Optional[float] = Field(0, description="退款赠送数量")
    payment_status: Optional[PaymentStatusType] = Field(
        PaymentStatusType.CREATED.value, description="付款状态")
    payment_channel: Optional[PaymentChannelType] = Field(
        PaymentChannelType.WECHATPAY.value, description="支付渠道")
    payment_time: Optional[datetime] = Field(None, description="付款时间")
    created_at: Optional[datetime] = None


class BalanceRechargeListResponse(BaseModel):
    total: int
    items: List[BalanceRechargeItem]


class BalanceRechargeOutListResponse(BaseModel):
    total: int
    items: List[BalanceRechargeOutItem]


class BalanceRechargeSearchQuery(PaginationParams):
    user_id: Optional[int] = Field(None, description="用户ID")
    trade_no: Optional[str] = Field(None, description="交易号")
    payment_channel: Optional[PaymentChannelType] = Field(None, description="支付渠道")
    payment_status: Optional[PaymentStatusType] = Field(None, description="付款状态")
    payment_start: Optional[datetime] = Field(None, description="付款时间开始")
    payment_end: Optional[datetime] = Field(None, description="付款时间结束")
    created_start: Optional[datetime] = Field(None, description="创建时间开始")
    created_end: Optional[datetime] = Field(None, description="创建时间结束")
