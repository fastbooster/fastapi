#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:15

import re

from typing import Optional
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
    phone: Optional[str] = None
    email: Optional[str] = None
    pid: Optional[int] = -1
    role_id: Optional[int] = -1
    status: Optional[int] = -1


class BaseUserForm(BaseModel):
    phone: str = Field(None, description="手机")
    email: EmailStr = Field(None, description="邮箱")
    password: Optional[str] = None

    @validator("phone")
    def validate_cell_phone_number(cls, v):
        match = re.match(r'^1\d{10}$', v)
        if len(v) != 11:
            raise ValueError('手机号码长度必须为 11 位')
        elif match is None:
            raise ValueError('手机号码格式不正确')
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('密码不能少于 6 位')
        if not re.search("[0-9]", v) or not re.search("[a-zA-Z]", v):
            raise ValueError('密码必须包含数字和字母')
        return v


class UserAddForm(BaseUserForm):
    phone: str = Field(None, description='与 email 二者必填其一')
    email: EmailStr = Field(None, description='与 phone 二者必填其一')
    nickname: str
    password: str
    gender: Optional[GenderType] = GenderType.UNKNOWN
    role_id: Optional[int] = 0
    join_from: Optional[JoinFromType] = Field(None, description='注册来源')
    join_ip: str = Field(None, description='注册IP')


class UserEditForm(BaseUserForm):
    id: int
    nickname: Optional[str] = None
    gender: Optional[GenderType] = GenderType.UNKNOWN
    role_id: Optional[int] = -1
