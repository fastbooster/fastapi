#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 19:48

import traceback

from fastapi import APIRouter, HTTPException, Depends, Request

from app.core.log import logger
from app.core.security import check_permission, get_current_user_id
from app.services import user as UserService

from app.schemas.schemas import ResponseSuccess
from app.schemas.user import UserSearchQuery, UserQuickSearchQuery, UserItem, UserListResponse, UserQuickListResponse, JoinFromType

router = APIRouter()


@router.get("/users", response_model=UserListResponse, dependencies=[Depends(check_permission('UserList'))], summary="用户列表")
def lists(params: UserSearchQuery = Depends()):
    return UserService.get_user_list(params)


@router.get("/users/quick_search", response_model=UserQuickListResponse, dependencies=[Depends(check_permission('UserList'))], summary="用户快速搜索，用于前端下拉列表")
def lists(params: UserQuickSearchQuery = Depends()):
    return UserService.get_user_quick_list(params)


@router.get("/users/{id}", response_model=UserItem, dependencies=[Depends(check_permission('UserList'))], summary="用户详情",)
def detail(id: int):
    user = UserService.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/users", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))], summary="添加用户")
def add(params: UserItem, request: Request):
    try:
        params.join_from = JoinFromType.BACKEND_ADMIN
        params.join_ip = request.client.host
        UserService.add_user(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加用户失败')


@router.put("/users/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))], summary="编辑用户")
def edit(id: int, params: UserItem):
    try:
        params.id = id
        UserService.edit_user(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑用户失败')


@router.delete("/users/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))], summary="删除用户",)
def delete(id: int, curret_user_id: int = Depends(get_current_user_id)):
    if id == curret_user_id:
        raise HTTPException(status_code=403, detail='不能删除自己')
    try:
        UserService.delete_user(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除用户失败')
