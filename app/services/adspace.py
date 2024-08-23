#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: adspace.py
# Author: FastBooster Generator
# Time: 2024-08-23 18:45


from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session
from app.models.cms import AdspaceModel
from app.schemas.adspace import AdspaceForm, SearchQuery
from app.schemas.schemas import StatusType


def get(id: int) -> AdspaceModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(AdspaceModel).filter(AdspaceModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(AdspaceModel).order_by(desc('id'))
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: AdspaceForm) -> None:
    with get_session() as db:
        if isinstance(params.status, StatusType):
            params.status = params.status.value
        current_model = AdspaceModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)


def update(id: int, params: AdspaceForm) -> None:
    with get_session() as db:
        current_model = db.query(AdspaceModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'广告位不存在(id={id})')

        if isinstance(params.status, StatusType):
            params.status = params.status.value

        current_model.from_dict(params.__dict__)
        db.commit()
        db.refresh(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(AdspaceModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'广告位不存在(id={id})')
        db.delete(current_model)
        db.commit()
