#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 23:29

from loguru import logger

from datetime import datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, validator

from app.schemas.schemas import StatusType, PaginationParams


class PaymentConfigItem(BaseModel):
    id: Optional[int] = Field(None, ge=0, description="ID")
    channel_id: Optional[int] = Field(None, ge=1, description="支付渠道ID")
    name: str = Field(None, min_length=1, max_length=50, description="对外显示的名称，如：微信支付或支付通道1")
    appname: Optional[str] = Field(None, min_length=1, max_length=50, description="支付平台APP名称")
    appid: str = Field(None, min_length=1, max_length=50, description="支付平台APPID")
    mchid: Optional[str] = Field(None, min_length=1, max_length=50, description="支付平台商户ID")
    miniappid: Optional[str] = Field(None, min_length=1, max_length=50, description="小程序ID, 微信支付专用")
    app_public_cert: Optional[str] = Field(None, description="应用公钥")
    app_private_key: Optional[str] = Field(None, description="应用私钥")
    app_secret_key: Optional[str] = Field(None, description="应用密钥")
    platform_public_cert: Optional[str] = Field(None, description="平台公钥")
    asc_sort_order: Optional[int] = None
    status: Optional[StatusType] = StatusType.ENABLED.value
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaymentConfigListResponse(BaseModel):
    total: int
    items: List[PaymentConfigItem]


class PaymentConfigSearchQuery(PaginationParams):
    channel_id: Optional[Union[int, str]] = None
    name: Optional[str] = None
    status: Optional[StatusType] = None

    @validator("channel_id")
    def validate_int(cls, v: Any) -> int | None:
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                logger.info(f'尝试将GET参数转换为整型失败: {type(v)}')
                return None
        if isinstance(v, (int, float)) and isinstance(int(v), int):
            return int(v)
        return v if isinstance(v, int) else None
