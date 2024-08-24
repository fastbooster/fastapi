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
    CROP = 'crop'  # 企业号
    OFFIACCOUNT = 'offiaccount'  # 公众号 (服务号/订阅号)


class WechatBase(BaseModel):
    """基础数据模型"""
    type: Optional[WechatType] = Field(None, description='类型')
    appid: Optional[str] = Field(None, description='AppID')
    appname: Optional[str] = Field(None, description='AppName')
    appsecret: Optional[str] = Field(None, description='AppSecret')
    token: Optional[str] = Field(None, description='Token')
    aeskey: Optional[str] = Field(None, description='AesKey')
    status: Optional[StatusType] = Field(None, description='状态')


class WechatForm(WechatBase):
    """表单数据模型"""
    pass


class WechatItem(WechatBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class WechatPublicItem(BaseModel):
    """公开数据模型"""
    type: Optional[WechatType] = Field(None, description='类型')
    appid: Optional[str] = Field(None, description='AppID')
    appname: Optional[str] = Field(None, description='AppName')
    status: Optional[StatusType] = Field(None, description='状态')
    created_at: datetime = Field(None, description="创建时间")


class WechatListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[WechatItem]


class WechatPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[WechatPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    type: Optional[WechatType] = None
    appid: Optional[str] = None
    appname: Optional[str] = None
