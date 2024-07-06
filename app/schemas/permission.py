#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permission.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 19:49

from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel


class PermissionItem(BaseModel):
    id: Optional[int] = 0
    pid: Optional[int] = 0
    name: str
    icon: Optional[str] = None
    component_name: Optional[str] = None
    asc_sort_order: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PermissionParentItem(PermissionItem):
    children: Optional[List[PermissionItem]] = None


class PermissionListResponse(BaseModel):
    total: int
    items: List[PermissionParentItem]
