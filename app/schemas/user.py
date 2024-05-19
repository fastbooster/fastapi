#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:15

from typing import Optional

from pydantic import BaseModel
from enum import Enum

from app.schemas.schemas import PaginationParams


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
