#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 19:48

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends, Request

from app.core.security import check_permission, get_current_user_id
from app.services import user as UserService
from app.core.mysql import get_session

from app.schemas.user import UserSearchQuery, UserAddForm, UserEditForm, JoinFromType
from app.constants.constants import RESPONSE_OK

router = APIRouter()


@router.get("/users", dependencies=[Depends(check_permission('UserList'))], summary="用户列表")
def user_list(params: UserSearchQuery = Depends()):
    return UserService.get_user_list(params)


@router.get("/users/{id}", dependencies=[Depends(check_permission('UserList'))], summary="用户详情",)
def user_detail(id: int):
    user = UserService.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/users", dependencies=[Depends(check_permission('UserList'))], summary="添加用户")
def add_user(params: UserAddForm, request: Request):
    try:
        params.join_from = JoinFromType.BACKEND_ADMIN
        params.join_ip = request.client.host
        UserService.add_user(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加用户失败：{e}')
        raise HTTPException(status_code=500, detail='添加用户失败')
    return RESPONSE_OK


@router.put("/users", dependencies=[Depends(check_permission('UserList'))], summary="编辑用户")
def edit_user(params: UserEditForm):
    try:
        UserService.edit_user(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑用户失败：{e}')
        raise HTTPException(status_code=500, detail='编辑用户失败')
    return RESPONSE_OK


@router.delete("/users/{id}", dependencies=[Depends(check_permission('UserList'))], summary="删除用户",)
def delete_user(id: int, curret_user_id: int = Depends(get_current_user_id)):
    if id == curret_user_id:
        raise HTTPException(status_code=403, detail='不能删除自己')
    try:
        UserService.delete_user(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除用户失败：{e}')
        raise HTTPException(status_code=500, detail='删除用户失败')
    return RESPONSE_OK
