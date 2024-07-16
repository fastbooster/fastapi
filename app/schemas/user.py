#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:15

import re

from loguru import logger

from datetime import datetime
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

from app.schemas.schemas import PaginationParams


class GenderType(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    UNKNOWN = 'Unknown'


class JoinFromType(Enum):
    '''注册来源'''
    FRONTEND_PORTAL = 1000  # 门户
    FRONTEND_WXOA = 1001  # 微信公众号
    FRONTEND_WXMP = 1002  # 微信小程序
    BACKEND_CONSOLE = 2000  # 控制台命令行
    BACKEND_ADMIN = 2001  # 后台管理


class ChangePwdForm(BaseModel):
    """修改密码表单"""
    old_pwd: str
    new_pwd: str


class UserSearchQuery(PaginationParams):
    id: Optional[int | str] = Field(None, description="ID")
    pid: Optional[int | str] = Field(None, description="上级ID")
    role_id: Optional[int | str] = Field(None, description="角色ID")
    status: Optional[int | str] = Field(None, description="状态")
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    @validator("id", "pid", "role_id", "status")
    def validate_int(cls, v: Any) -> int | None:
        '''
        允许字符串类型，因为前端传过来的 id 可能是字符串，这里统一转换为 int
        如果转换失败，则返回 None，并记录日志
        '''
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                logger.info(f'尝试将GET参数转换为整型失败: {type(v)}')
                return None
        if isinstance(v, (int, float)) and isinstance(int(v), int):
            return int(v)
        return v if isinstance(v, int) else None


class BaseUserForm(BaseModel):
    phone: str = Field(None, description="手机")
    email: EmailStr = Field(None, description="邮箱")
    password: Optional[str] = None

    @validator("phone")
    def validate_cell_phone_number(cls, v):
        if not v:
            return None
        match = re.match(r'^1\d{10}$', v)
        if len(v) != 11:
            raise ValueError('手机号码长度必须为 11 位')
        elif match is None:
            raise ValueError('手机号码格式不正确')
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        if not v:
            return None
        if len(v) < 6:
            raise ValueError('密码不能少于 6 位')
        if not re.search("[0-9]", v) or not re.search("[a-zA-Z]", v):
            raise ValueError('密码必须包含数字和字母')
        return v


class UserItem(BaseUserForm):
    id: Optional[int] = 0
    pid: Optional[int] = 0
    agent_id: Optional[int] = 0
    phone_code: Optional[str] = '86'
    phone: Optional[str] = Field(None, description='与 email 二者必填其一')
    email: Optional[Union[EmailStr, str]] = Field(None, description='与 phone 二者必填其一')
    nickname: Optional[str] = None
    password: Optional[str] = Field(None, description='明文密码，用于注册用户')
    gender: Optional[GenderType] = GenderType.UNKNOWN
    avatar: Optional[str] = None
    promotion_code: Optional[str] = None
    status: Optional[int] = 1
    role_id: Optional[int] = 0
    auto_memo: Optional[str] = None
    back_memo: Optional[str] = None
    wechat_openid: Optional[str] = None
    join_from: Optional[JoinFromType] = Field(None, description='注册来源')
    join_ip: str = Field(None, description='注册IP')
    join_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    total: int
    items: List[UserItem]
