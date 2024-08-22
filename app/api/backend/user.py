#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: FastBooster Generator
# Time: 2024-08-22 21:06

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.schemas import ResponseSuccess
from app.schemas.user import UserForm, UserItem, SearchQuery, SimpleSearchQuery, UserListResponse, UserSimpleListResponse
from app.services import user

router = APIRouter()


@router.get("/users", response_model=UserListResponse, dependencies=[Depends(check_permission('UserList'))],
            summary="用户列表")
def lists(params: SearchQuery = Depends()):
    return user.lists(params)


@router.get("/users/quick_search", response_model=UserSimpleListResponse,
            dependencies=[Depends(check_permission('UserList'))], summary="用户快速搜索，用于前端下拉列表")
def quick_search(params: SimpleSearchQuery = Depends()):
    return user.simple_lists(params)


@router.get("/users/{id}", response_model=UserItem, dependencies=[Depends(check_permission('UserList'))],
            summary="用户详情", )
def detail(id: int):
    current_model = user.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="用户不存在")
    return current_model


@router.post("/users", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
             summary="添加用户")
def add(params: UserForm):
    try:
        user.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加用户失败')


@router.put("/users/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
            summary="编辑用户")
def update(id: int, params: UserForm):
    try:
        user.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑用户失败')


@router.delete("/users/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
               summary="删除用户")
def delete(id: int):
    try:
        user.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除用户失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除用户失败')
