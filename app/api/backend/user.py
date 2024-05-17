#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 19:48

from fastapi import APIRouter, HTTPException

from app.core.security import AuthChecker, get_current_user
from app.models.user import UserModel
from app.core.mysql import get_session

router = APIRouter()


@router.get("/users", summary="用户列表")
def user_list():
    pass


@router.get("/users/{user_id}", summary="用户详情")
def user_detail(user_id: int):
    pass
