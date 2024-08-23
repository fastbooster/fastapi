#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: FastBooster Generator
# Time: 2024-08-23 22:09

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.finance import PaymentStatusType, PaymentChannelType
from app.schemas.schemas import PaginationParams


class BalanceRechargeBase(BaseModel):
    """基础数据模型"""
    user_id: Optional[int] = Field(None, description='用户ID')
    trade_no: Optional[str] = Field(None, description='交易号')
    amount: Optional[Decimal] = Field(None, description='充值数量')
    price: Optional[Decimal] = Field(None, description='支付金额')
    gift_amount: Optional[Decimal] = Field(None, description='赠送数量')
    refund_amount: Optional[Decimal] = Field(None, description='退款数量')
    refund_gift_amount: Optional[Decimal] = Field(None, description='退款赠送数量')
    payment_status: Optional[PaymentStatusType] = Field(PaymentStatusType.CREATED.value, description='状态')
    payment_channel: Optional[PaymentChannelType] = Field(PaymentChannelType.WECHATPAY.value, description='支付渠道')
    payment_appid: Optional[str] = Field(None, description='支付APPID')
    payment_time: Optional[datetime] = Field(None, description='支付时间')
    payment_response: Optional[str] = Field(None, description='支付结果')
    refund_response: Optional[str] = Field(None, description='退款结果')
    audit_user_id: Optional[int] = Field(None, description='审核人员ID')
    audit_user_name: Optional[str] = Field(None, description='审核人员姓名')
    audit_reply: Optional[str] = Field(None, description='审核回复')
    audit_time: Optional[datetime] = Field(None, description='审核时间')
    audit_ip: Optional[str] = Field(None, description='审核人员IP地址')
    user_ip: Optional[str] = Field(None, description='用户充值时的IP地址')
    auto_memo: Optional[str] = Field(None, description='自动备注')
    back_memo: Optional[str] = Field(None, description='后台备注')


class BalanceRechargeForm(BalanceRechargeBase):
    """表单数据模型"""
    pass


class BalanceRechargeItem(BalanceRechargeBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class BalanceRechargePublicItem(BaseModel):
    """公开数据模型"""
    trade_no: str = Field(max_length=32, description="交易号")
    amount: float = Field(description="充值数量")
    price: float = Field(description="支付金额")
    gift_amount: Optional[float] = Field(0, description="赠送数量")
    refund_amount: Optional[float] = Field(0, description="退款数量")
    refund_gift_amount: Optional[float] = Field(0, description="退款赠送数量")
    payment_status: Optional[PaymentStatusType] = Field(PaymentStatusType.CREATED.value, description="付款状态")
    payment_channel: Optional[PaymentChannelType] = Field(PaymentChannelType.WECHATPAY.value, description="支付渠道")
    payment_time: Optional[datetime] = Field(None, description="付款时间")
    created_at: datetime


class BalanceRechargeListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[BalanceRechargeItem]


class BalanceRechargePublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[BalanceRechargePublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    user_id: Optional[int] = Field(None, description="用户ID")
    trade_no: Optional[str] = Field(None, description="交易号")
    payment_channel: Optional[PaymentChannelType] = Field(None, description="支付渠道")
    payment_status: Optional[PaymentStatusType] = Field(None, description="付款状态")
    payment_start: Optional[datetime] = Field(None, description="付款时间开始")
    payment_end: Optional[datetime] = Field(None, description="付款时间结束")
    created_start: Optional[datetime] = Field(None, description="创建时间开始")
    created_end: Optional[datetime] = Field(None, description="创建时间结束")
