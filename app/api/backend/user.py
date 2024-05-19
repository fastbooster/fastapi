#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 19:48

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import user as UserService
from app.core.mysql import get_session

from app.schemas.schemas import PaginationParams

router = APIRouter()


@router.get("/users", dependencies=[Depends(check_permission('UserList'))], summary="用户列表")
def user_list(params: PaginationParams = Depends()):
    return UserService.get_user_list(params)


@router.get("/users/{user_id}", dependencies=[Depends(check_permission('UserList'))], summary="用户详情",)
def user_detail(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user
