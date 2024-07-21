#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 01:26


from sqlalchemy import text
from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session

from app.models.user import RoleModel
from app.schemas.role import RoleItem, RoleSearchQuery, RoleListResponse


def get_role(id: int) -> RoleModel | None:
    with get_session(read_only=True) as db:
        role = db.query(RoleModel).filter(RoleModel.id == id).first()

    if role is not None:
        return role

    return None


def get_role_list(params: RoleSearchQuery) -> RoleListResponse:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(RoleModel).order_by(desc('id'))
        if params.name:
            query = query.filter(RoleModel.name.like(f'%{params.name}%'))
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add_role(params: RoleItem) -> bool:
    with get_session() as db:
        exists_count = db.query(RoleModel).filter(
            RoleModel.name == params.name).count()
        if exists_count > 0:
            raise ValueError('该角色名称已存在')

        role_model = RoleModel(
            name=params.name,
            permissions=params.permissions,
        )

        db.add(role_model)
        db.commit()
    return True


def edit_role(params: RoleItem) -> bool:
    with get_session() as db:
        role_model = db.query(RoleModel).filter_by(id=params.id).first()
        if role_model is None:
            raise ValueError(f'角色不存在(id={params.id})')

        exists_count = db.query(RoleModel).filter(RoleModel.name == params.name,
                                                  RoleModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError('该角色名称已存在')

        role_model.name = params.name
        role_model.permissions = params.permissions

        db.commit()

    return True


def delete_role(id: int) -> bool:
    with get_session() as db:
        role_model = db.query(RoleModel).filter_by(id=id).first()
        if role_model is None:
            raise ValueError(f'角色不存在(id={id})')

        conn = db.connection()
        conn.execute(text('update user_account set role_id=0 where role_id=:id'), {"id": id})

        db.delete(role_model)
        db.commit()

    return True
