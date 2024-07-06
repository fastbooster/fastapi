#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 01:13

from datetime import datetime

from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas.schemas import PaginationParams


class RoleItem(BaseModel):
    id: Optional[int] = 0
    name: str
    permissions: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RoleListResponse(BaseModel):
    total: int
    items: List[RoleItem]


class RoleSearchQuery(PaginationParams):
    name: Optional[str] = None
