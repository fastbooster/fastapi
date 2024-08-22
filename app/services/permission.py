#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: permission.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 19:56

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session
from app.models.user import PermissionModel


def get(id: int) -> PermissionModel | None:
    with get_session(read_only=True) as db:
        permission = db.query(PermissionModel).filter(
            PermissionModel.id == id).first()
        if permission is not None:
            return permission
        return None


def lists() -> dict:
    with get_session(read_only=True) as db:
        items = db.query(PermissionModel).order_by(
            asc(PermissionModel.id)).all()
        if not items:
            return {"total": 0, "items": []}

        final_items = []
        for item in items:
            if item.pid == 0:
                final_item_dict = item.__dict__.copy()  # 只对pid为0的项转换为字典
                children = []
                for sub_item in items:
                    if sub_item.pid == item.id:
                        children.append(sub_item.__dict__.copy())  # 对子项也转换为字典
                if children:
                    final_item_dict["children"] = children
                final_items.append(final_item_dict)
        return {"total": len(final_items), "items": final_items}
