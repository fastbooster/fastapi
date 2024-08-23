#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: banner.py
# Author: FastBooster Generator
# Time: 2024-08-23 19:52


import json

from sqlalchemy.sql.expression import asc, desc

from app.constants.constants import REDIS_AD_PREFIX
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.cms import BannerModel
from app.schemas.banner import PositionType, BannerForm, SearchQuery
from app.schemas.schemas import StatusType


def get(id: int) -> BannerModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(BannerModel).filter(BannerModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(BannerModel).order_by(desc('id'))
        if isinstance(params.id, int):
            query = query.filter_by(id=params.id)
        if isinstance(params.space_id, int):
            query = query.filter_by(space_id=params.space_id)
        if isinstance(params.status, StatusType):
            query = query.filter_by(status=params.status.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: BannerForm) -> None:
    with get_session() as db:
        if isinstance(params.position, PositionType):
            params.position = params.position.value
        if isinstance(params.status, StatusType):
            params.status = params.status.value
        current_model = BannerModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update(id: int, params: BannerForm) -> None:
    with get_session() as db:
        current_model = db.query(BannerModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'广告资源不存在(id={id})')
        if isinstance(params.position, PositionType):
            params.position = params.position.value
        if isinstance(params.status, StatusType):
            params.status = params.status.value
        current_model.from_dict(params.__dict__)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(BannerModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'广告资源不存在(id={id})')
        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def update_cache(current_model: BannerModel, is_delete: bool = False) -> None:
    with get_redis() as redis:
        if is_delete or current_model.status == StatusType.DISABLED:
            redis.hdel(REDIS_AD_PREFIX + str(current_model.adspace_id), current_model.id)
        else:
            redis.hset(REDIS_AD_PREFIX + str(current_model.adspace_id), current_model.id,
                       json.dumps(current_model.__dict__, default=str))


def rebuild_cache() -> None:
    with get_redis() as redis:
        keys = redis.keys(REDIS_AD_PREFIX + '*')
        if keys:
            redis.delete(*keys)
    with get_session(read_only=True) as db:
        items = db.query(BannerModel).order_by(asc('id')).all()
        for item in items:
            update_cache(item)
