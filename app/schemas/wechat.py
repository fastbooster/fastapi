#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/25 16:57

from datetime import datetime

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.schemas import StatusType, PaginationParams


class WechatType(Enum):
    APP = 'app'  # 小程序
    OFFIACCOUNT = 'offiaccount'  # 公众号 (服务号/订阅号)
    CROP = 'crop'  # 企业号


class WechatItem(BaseModel):
    id: Optional[int] = 0
    type: Optional[WechatType] = Field(None, description='类型')
    appid: Optional[str] = Field(None, description='AppID')
    appname: Optional[str] = Field(None, description='AppName')
    appsecret: Optional[str] = Field(None, description='AppSecret')
    token: Optional[str] = Field(None, description='Token')
    aeskey: Optional[str] = Field(None, description='AesKey')
    status: Optional[StatusType] = Field(None, description='状态')
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WechatOutItem(BaseModel):
    type: Optional[WechatType] = Field(None, description='类型')
    appid: Optional[str] = Field(None, description='AppID')
    appname: Optional[str] = Field(None, description='AppName')
    status: Optional[StatusType] = Field(None, description='状态')
    created_at: Optional[datetime] = None


class WechatListResponse(BaseModel):
    total: int
    items: List[WechatItem]


class WechatOutListResponse(BaseModel):
    total: int
    items: List[WechatOutItem]


class WechatSearchQuery(PaginationParams):
    type: Optional[WechatType] = None
    appid: Optional[str] = None
    appname: Optional[str] = None
