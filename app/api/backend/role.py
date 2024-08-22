#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 01:57

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.services import role

from app.schemas.schemas import ResponseSuccess
from app.schemas.role import RoleForm, RoleItem, SearchQuery, RoleListResponse

router = APIRouter()


@router.get("/roles", response_model=RoleListResponse, dependencies=[Depends(check_permission('RoleList'))], summary="角色列表")
def lists(params: SearchQuery = Depends()):
    return role.lists(params)


@router.get("/roles/{id}", response_model=RoleItem, dependencies=[Depends(check_permission('RoleList'))], summary="角色详情",)
def detail(id: int):
    current_role = role.get(id)
    if not current_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return current_role


@router.post("/roles", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="添加角色")
def add(params: RoleForm):
    try:
        role.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加角色失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加角色失败')


@router.put("/roles/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="编辑角色")
def update(id: int, params: RoleForm):
    try:
        role.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑角色失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑角色失败')


@router.delete("/roles/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="删除角色",)
def delete(id: int):
    try:
        role.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除角色失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除角色失败')
