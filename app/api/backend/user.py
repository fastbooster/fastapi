#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 19:48

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import AuthChecker
from app.services import user as UserService
from app.core.mysql import get_session

router = APIRouter()


@router.get("/users", summary="用户列表")
def user_list():
    pass


@router.get("/users/{user_id}", dependencies=[Depends(AuthChecker())], summary="用户详情")
def user_detail(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
