#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permission.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 19:56

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session

from app.models.user import PermissionModel
from app.schemas.permission import PermissionListResponse


def get_permission(id: int) -> PermissionModel | None:
    with get_session() as db:
        permission = db.query(PermissionModel).filter(
            PermissionModel.id == id).first()
    if permission is not None:
        return permission
    return None


def get_permission_list() -> PermissionListResponse:
    with get_session() as db:
        query = db.query(PermissionModel).order_by(asc('id'))

    items = query.all()
    if len(items) == 0:
        return {"total": 0, "items": []}

    final_items = []
    items_dict = [item.__dict__ for item in items]
    items_map = {item["id"]: item for item in items_dict}
    for item in items_dict:
        if item["pid"] == 0:
            final_items.append(item)
        else:
            parent = items_map.get(item["pid"])
            if parent:
                if "children" not in parent:
                    parent["children"] = []
            parent["children"].append(item)

    result = [item for item in final_items if item["pid"] == 0]

    return {"total": len(result), "items": result}
