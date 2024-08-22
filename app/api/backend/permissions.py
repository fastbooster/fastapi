#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permissions.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 20:43

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.schemas.permission import PermissionItem, PermissionNestResponse
from app.services import permission

router = APIRouter()


@router.get("/permissions", response_model=PermissionNestResponse,
            dependencies=[Depends(check_permission('PermissionList'))], summary="权限列表")
def lists():
    return permission.lists()


@router.get("/permissions/{id}", response_model=PermissionItem,
            dependencies=[Depends(check_permission('PermissionList'))], summary="权限详情")
def detail(id: int):
    current_model = permission.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="权限不存在")
    return current_model
