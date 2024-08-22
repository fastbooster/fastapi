#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: FastBooster Generator
# Time: 2024-08-22 21:06

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr, field_validator

from app.schemas.schemas import StatusType, PaginationParams


class GenderType(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    UNKNOWN = 'Unknown'


class JoinFromType(Enum):
    """注册来源"""
    DEFAULT = 0  # 未知
    FRONTEND_PORTAL = 1000  # 门户
    FRONTEND_WXOA = 1001  # 微信公众号
    FRONTEND_WXMP = 1002  # 微信小程序
    FRONTEND_ANDROID = 1004  # 安卓APP
    FRONTEND_IOS = 1004  # iOS APP
    BACKEND_CONSOLE = 2000  # 控制台命令行
    BACKEND_ADMIN = 2001  # 后台管理


class UserBase(BaseModel):
    """基础数据模型"""
    pid: Optional[int] = Field(None, description='所属上级')
    agent_id: Optional[int] = Field(None, description='所属代理')
    phone_code: Optional[str] = Field(None, description='手机代码')
    phone: Optional[str] = Field(None, description='手机')
    email: Optional[EmailStr] = Field(None, description='邮箱')
    nickname: Optional[str] = Field(None, description='昵称')
    gender: Optional[GenderType] = Field(None, description='性别')
    avatar: Optional[str] = Field(None, description='头像')
    promotion_code: Optional[str] = Field(None, description='推广码')
    password_salt: Optional[str] = Field(None, description='密码盐')
    password_hash: Optional[str] = Field(None, description='密码哈希')
    role_id: Optional[int] = Field(None, description='角色ID')
    is_admin: Optional[int] = Field(None, description='是否管理员')
    is_robot: Optional[int] = Field(None, description='是否机器人')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')
    auto_memo: Optional[str] = Field(None, description='自动备注')
    back_memo: Optional[str] = Field(None, description='后台备注')
    wechat_openid: Optional[str] = Field(None, description='OpenID')
    wechat_unionid: Optional[str] = Field(None, description='UnionID')
    wechat_refresh_token: Optional[str] = Field(None, description='微信RefreshToken')
    wechat_access_token: Optional[str] = Field(None, description='微信AccessToken')
    wechat_access_token_expired_at: Optional[int] = Field(None, description='微信AccessToken过期时间')
    join_from: Optional[JoinFromType] = Field(None, description='注册来源')
    join_ip: Optional[str] = Field(None, description='注册IP')
    join_at: Optional[datetime] = Field(None, description='注册时间')


class UserForm(UserBase):
    """表单数据模型"""
    phone: Optional[str] = Field(None, description='与 email 二者必填其一')
    email: Optional[EmailStr] = Field(None, description='与 phone 二者必填其一')
    password: Optional[str] = Field(None, min_length=6, description="明文密码")

    # noinspection PyNestedDecorators
    @field_validator("password", mode="before")
    @classmethod
    def validate_password_strength(cls, v):
        if not v:
            return None
        if not re.search("[0-9]", v) or not re.search("[a-zA-Z]", v):
            raise ValueError('密码必须包含数字和字母')
        return v


class UserItem(UserBase):
    """数据库全量字段模型"""
    id: int = Field(description="ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")


class UserPublicItem(BaseModel):
    """公开数据模型"""
    phone_code: Optional[str] = Field(None, description='手机代码')
    phone: Optional[str] = Field(None, description='手机')
    email: Optional[EmailStr] = Field(None, description='邮箱')
    nickname: Optional[str] = Field(None, description='昵称')
    gender: Optional[GenderType] = Field(None, description='性别')
    avatar: Optional[str] = Field(None, description='头像')
    promotion_code: Optional[str] = Field(None, description='推广码')
    status: Optional[StatusType] = Field(None, description='状态: enabled/disabled')
    wechat_openid: Optional[str] = Field(None, description='OpenID')
    wechat_unionid: Optional[str] = Field(None, description='UnionID')
    join_from: Optional[JoinFromType] = Field(None, description='注册来源')
    join_ip: Optional[str] = Field(None, description='注册IP')
    join_at: Optional[datetime] = Field(None, description='注册时间')


class UserListResponse(BaseModel):
    """响应数据模型"""
    total: int
    items: List[UserItem]


class UserPublicListResponse(BaseModel):
    """公开响应模型"""
    total: int
    items: List[UserPublicItem]


class SearchQuery(PaginationParams):
    """搜索查询参数"""
    id: Optional[int] = None
    pid: Optional[int] = None
    role_id: Optional[int] = None
    status: Optional[int] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class ChangePwdForm(BaseModel):
    """修改密码表单"""
    old_pwd: str = Field(description='旧密码')
    new_pwd: str = Field(min_length=6, description='新密码')

    # noinspection PyNestedDecorators
    @field_validator("new_pwd", mode="before")
    @classmethod
    def validate_password_strength(cls, v):
        if not v:
            return None
        if not re.search("[0-9]", v) or not re.search("[a-zA-Z]", v):
            raise ValueError('密码必须包含数字和字母')
        return v


class SimpleSearchQuery(BaseModel):
    keyword: int | str = Field(None, description="关键字")
    limit: Optional[int] = Field(10, ge=1, le=100, description="数量")


class UserSimpleItem(BaseModel):
    id: int = Field(None, description="ID")
    nickname: Optional[str] = Field(None, description="昵称")
    phone: Optional[str] = Field(None, description="手机")
    email: Optional[EmailStr] = Field(None, description="邮箱")


class UserSimpleListResponse(BaseModel):
    total: int
    items: List[UserSimpleItem]
