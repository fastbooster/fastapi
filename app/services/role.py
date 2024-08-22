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
from app.schemas.role import RoleForm, SearchQuery


def get(id: int) -> RoleModel | None:
    with get_session(read_only=True) as db:
        role = db.query(RoleModel).filter(RoleModel.id == id).first()

    if role is not None:
        return role

    return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(RoleModel).order_by(desc('id'))
        if params.name:
            query = query.filter(RoleModel.name.like(f'%{params.name}%'))
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: RoleForm) -> None:
    with get_session() as db:
        exists_count = db.query(RoleModel).filter(
            RoleModel.name == params.name).count()
        if exists_count > 0:
            raise ValueError('该角色名称已存在')
        current_model = RoleModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()


def update(id: int, params: RoleForm) -> None:
    with get_session() as db:
        current_model = db.query(RoleModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'角色不存在(id={id})')

        exists_count = db.query(RoleModel).filter(RoleModel.name == params.name, RoleModel.id != id).count()
        if exists_count > 0:
            raise ValueError('该角色名称已存在')

        current_model.from_dict(params.__dict__)
        db.commit()


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(RoleModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'角色不存在(id={id})')

        conn = db.connection()
        conn.execute(text('update user_account set role_id=0 where role_id=:id'), {"id": id})

        db.delete(current_model)
        db.commit()
