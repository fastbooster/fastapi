#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 20:13

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import AuthChecker, get_current_user_from_cache
from app.models.user import UserModel
from app.services import user as UserService
from app.core.mysql import get_session

router = APIRouter()


@router.get("/user/me", summary="我的详情")
def my_detail(user_data: dict = Depends(get_current_user_from_cache)):
    return UserService.safe_whitelist_fields(user_data)
