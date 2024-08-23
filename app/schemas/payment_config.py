#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: FastBooster Generator
# Time: 2024-08-23 13:30

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, MysqlBoolType, PaginationParams


class PaymentConfigBase(BaseModel):
    """基础数据模型"""
    channel_id: Optional[int] = Field(None, ge=1, description='支付渠道ID')
    channel_key: Optional[str] = Field(None, description='支付渠道KEY')
    name: Optional[str] = Field(None, description='对外显示的名称，如：微信支付或支付通道1')
    appname: Optional[str] = Field(None, description='支付平台APP名称')
    appid: Optional[str] = Field(None, description='支付平台APPID')
    mchid: Optional[str] = Field(None, description='支付平台商户ID')
    miniappid: Optional[str] = Field(None, description='小程序APPID')
    app_public_cert: Optional[str] = Field(None, description='应用公钥')
    app_private_key: Optional[str] = Field(None, description='应用私钥')
    app_secret_key: Optional[str] = Field(None, description='应用密钥')
    platform_public_cert: Optional[str] = Field(None, description='平台公钥')
    locked: Optional[MysqlBoolType] = Field(None, description='锁定: yes/no')
    asc_sort_order: Optional[int] = Field(None, description='排序')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')


class PaymentConfigForm(PaymentConfigBase):
    """表单数据模型"""
    channel_id: int = Field(ge=1, description='支付渠道ID')
    name: str = Field(description='对外显示的名称，如：微信支付或支付通道1')
    appid: str = Field(description='支付平台APPID')


class PaymentConfigStatusForm(BaseModel):
    """更新状态表单模型"""
    status: StatusType = Field(description='状态: enabled/disabled')


class PaymentConfigItem(PaymentConfigBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class PaymentConfigPublicItem(BaseModel):
    """公开数据模型"""
    channel_id: int = Field(None, ge=1, description="支付渠道ID")
    channel_key: Optional[str] = Field(None, description="支付渠道KEY")
    name: str = Field(None, min_length=1, max_length=50, description="对外显示的名称，如：微信支付或支付通道1")
    appname: Optional[str] = Field(None, min_length=1, max_length=50, description="支付平台APP名称")
    appid: str = Field(None, min_length=1, max_length=50, description="支付平台APPID")
    mchid: Optional[str] = Field(None, min_length=1, max_length=50, description="支付平台商户ID")
    miniappid: Optional[str] = Field(None, min_length=1, max_length=50, description="小程序ID, 微信支付专用")
    locked: Optional[MysqlBoolType] = MysqlBoolType.NO.value
    asc_sort_order: Optional[int] = None
    status: Optional[StatusType] = StatusType.ENABLED.value


class PaymentConfigListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[PaymentConfigItem]


class PaymentConfigPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[PaymentConfigPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    channel_id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[StatusType] = None
