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


class UserAddForm(BaseModel):
    phone: str = Field(None, description="与 email 二者必填其一")
    email: EmailStr = Field(None, description="与 phone 二者必填其一")
    nickname: str
    password: str
    gender: GenderType = GenderType.UNKNOWN
    role_id: Optional[int] = 0

    @validator("phone")
    def validate_cell_phone_number(cls, v):
        match = re.match(r'^1\d{10}$', v)
        if len(v) != 11:
            raise ValueError('手机号码长度必须为 11 位')
        elif match is None:
            raise ValueError('手机号码格式不正确')
        return v
