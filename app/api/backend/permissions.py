#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permissions.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 20:43

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import permission as PermissionService

from app.schemas.schemas import ResponseSuccess
from app.schemas.permission import PermissionItem, PermissionListResponse

router = APIRouter()


@router.get("/permissions", response_model=PermissionListResponse, dependencies=[Depends(check_permission('PermissionList'))], summary="权限列表")
def lists():
    return PermissionService.get_permission_list()
