#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: FastBooster Generator
# Time: 2024-08-23 12:11


import json

from sqlalchemy.sql.expression import asc, desc, or_

from app.constants.constants import REDIS_PAYMENT_CHANNEL
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.payment_settings import PaymentChannelModel
from app.schemas.payment_channel import PaymentChannelForm, SearchQuery
from app.schemas.schemas import StatusType, MysqlBoolType
from app.utils.helper import serialize_datetime


def get(id: int) -> PaymentChannelModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(PaymentChannelModel).filter(PaymentChannelModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(PaymentChannelModel).order_by(desc('id'))
        if params.key:
            query = query.filter(PaymentChannelModel.key.like(f'%{params.key}%'))
        if params.name:
            query = query.filter(PaymentChannelModel.name.like(f'%{params.name}%'))
        if isinstance(params.status, StatusType):
            query = query.filter(PaymentChannelModel.status == params.status.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: PaymentChannelForm) -> None:
    with get_session() as db:
        exists_count = db.query(PaymentChannelModel).filter(
            or_(
                PaymentChannelModel.key == params.key,
                PaymentChannelModel.name == params.name
            )).count()
        if exists_count > 0:
            raise ValueError('KEY或名称已存在')

        last_item = db.query(PaymentChannelModel).order_by(desc('id')).first()
        params.asc_sort_order = 1 if last_item is None else last_item.asc_sort_order + 1

        if isinstance(params.status, StatusType):
            params.status = params.status.value
        if isinstance(params.locked, MysqlBoolType):
            params.locked = params.locked.value

        current_model = PaymentChannelModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update(id: int, params: PaymentChannelForm) -> None:
    with get_session() as db:
        current_model = db.query(PaymentChannelModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'支付渠道不存在(id={id})')

        exists_count = db.query(PaymentChannelModel).filter(or_(
            PaymentChannelModel.key == params.key,
            PaymentChannelModel.name == params.name
        ), PaymentChannelModel.id != id).count()
        if exists_count > 0:
            raise ValueError('KEY或名称已存在')

        if isinstance(params.status, StatusType):
            params.status = params.status.value

        # current_model.key = params.key # 禁止修改 key, 防止缓存溢出
        # current_model.locked = params.locked.value # 禁止更新
        current_model.name = params.name
        current_model.icon = params.icon
        current_model.status = params.status

        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(PaymentChannelModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'支付渠道不存在(id={id})')
        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def update_cache(current_model: PaymentChannelModel, is_delete: bool = False) -> None:
    """注意：模型的 key 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出"""
    with get_redis() as redis:
        if not is_delete:
            params = current_model.to_dict()
            params['created_at'] = serialize_datetime(params['created_at'])
            params['updated_at'] = serialize_datetime(params['updated_at'])
            redis.hset(REDIS_PAYMENT_CHANNEL, current_model.key, json.dumps(params))
        else:
            redis.hdel(REDIS_PAYMENT_CHANNEL, current_model.appid)


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        with get_redis() as redis:
            items = db.query(PaymentChannelModel).order_by(asc('asc_sort_order')).all()
            redis.delete(REDIS_PAYMENT_CHANNEL)
            for item in items:
                update_cache(item)
