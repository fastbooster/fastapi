#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permissions.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 20:43

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.services import permission as PermissionService

from app.schemas.schemas import ResponseSuccess
from app.schemas.permission import PermissionItem, PermissionListResponse

router = APIRouter()


@router.get("/permissions", response_model=PermissionListResponse, dependencies=[Depends(check_permission('PermissionList'))], summary="权限列表")
def lists():
    return PermissionService.get_permission_list()


@router.get("/permissions/{id}", response_model=PermissionItem, dependencies=[Depends(check_permission('RoleList'))], summary="权限详情",)
def detail(id: int):
    permission = PermissionService.get_permission(id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    return permission
