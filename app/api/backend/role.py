#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 01:57

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import role as RoleService

from app.schemas.schemas import ResponseSuccess
from app.schemas.role import RoleItem, RoleSearchQuery, RoleListResponse

router = APIRouter()


@router.get("/roles", response_model=RoleListResponse, dependencies=[Depends(check_permission('RoleList'))], summary="角色列表")
def lists(params: RoleSearchQuery = Depends()):
    return RoleService.get_role_list(params)


@router.get("/roles/{id}", response_model=RoleItem, dependencies=[Depends(check_permission('RoleList'))], summary="角色详情",)
def detail(id: int):
    role = RoleService.get_role(id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    return role


@router.post("/roles", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="添加角色")
def add(params: RoleItem):
    try:
        RoleService.add_role(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加角色失败：{e}')
        raise HTTPException(status_code=500, detail='添加角色失败')
    return ResponseSuccess


@router.put("/roles/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="编辑角色")
def edit(id: int, params: RoleItem):
    try:
        params.id = id
        RoleService.edit_role(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑角色失败：{e}')
        raise HTTPException(status_code=500, detail='编辑角色失败')
    return ResponseSuccess


@router.delete("/roles/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RoleList'))], summary="删除角色",)
def delete(id: int):
    try:
        RoleService.delete_role(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除角色失败：{e}')
        raise HTTPException(status_code=500, detail='删除角色失败')
    return ResponseSuccess
