#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ${file_name}
# Author: FastBooster Generator
# Time: ${create_time}


import json

from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session
from app.models.${module_name} import ${model_name}
from app.schemas.schemas import StatusType, MysqlBoolType
from app.schemas.${snake_name} import ${model}Form, SearchQuery


def get(id: int) -> ${model_name} | None:
    with get_session(read_only=True) as db:
        current_model = db.query(${model_name}).filter(${model_name}.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(${model_name}).order_by(desc('id'))
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: ${model}Form) -> None:
    with get_session() as db:
        current_model = ${model_name}()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update(id: int, params: ${model}Form) -> None:
    with get_session() as db:
        current_model = db.query(${model_name}).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'${name}不存在(id={id})')

        current_model.from_dict(params.__dict__)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(${model_name}).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'${name}不存在(id={id})')
        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def update_cache(current_model: ${model_name}, is_delete: bool = False) -> None:
    pass


def rebuild_cache() -> None:
    pass
