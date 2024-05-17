#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:15

from typing import Optional

from pydantic import BaseModel
from enum import Enum


class ChangePwdForm(BaseModel):
    """修改密码表单"""
    old_pwd: str
    new_pwd: str


class ListForm(BaseModel):
    """列表表单"""
    page: Optional[int] = 1
    size: Optional[int] = 10
    export: Optional[int] = 0
