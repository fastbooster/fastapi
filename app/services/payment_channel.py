#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 11:01

import json
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.core.redis import get_redis

from app.constants.constants import REDIS_PAYMENT_CHANNEL

from app.models.payment_settings import PaymentChannelModel, PaymentConfigModel
from app.schemas.schemas import StatusType, MysqlBoolType
from app.schemas.payment_channel import PaymentChannelItem, PaymentChannelSearchQuery, PaymentChannelListResponse


def get_payment_channel(id: int) -> PaymentChannelModel | None:
    with get_session() as db:
        item = db.query(PaymentChannelModel).filter(
            PaymentChannelModel.id == id).first()

    if item is not None:
        return item

    return None


def get_payment_channel_list(params: PaymentChannelSearchQuery) -> PaymentChannelListResponse:
    total = -1
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(PaymentChannelModel).order_by(asc('asc_sort_order'))
        if params.key:
            query = query.filter(
                PaymentChannelModel.key.like(f'%{params.key}%'))
        if params.name:
            query = query.filter(
                PaymentChannelModel.name.like(f'%{params.name}%'))
        if isinstance(params.status, StatusType):
            query = query.filter(
                PaymentChannelModel.status == params.status.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return {"total": total, "items": query.all()}


def add_payment_channel(params: PaymentChannelItem) -> bool:
    with get_session() as db:
        exists_count = db.query(PaymentChannelModel).filter(
            or_(
                PaymentChannelModel.key == params.key,
                PaymentChannelModel.name == params.name
            )).count()
        if exists_count > 0:
            raise ValueError('KEY或名称已存在')

        last_item = db.query(PaymentChannelModel).order_by(desc('id')).first()
        asc_sort_order = 1 if last_item is None else last_item.asc_sort_order + 1

        model = PaymentChannelModel(
            key=params.key,
            name=params.name,
            icon=params.icon,
            locked=MysqlBoolType.NO.value,  # 不允许添加锁定的渠道
            asc_sort_order=asc_sort_order,
            status=params.status.value,
        )

        db.add(model)
        db.commit()

        params.id = model.id
        update_cache(params.model_dump())

    return True


def edit_payment_channel(params: PaymentChannelItem) -> bool:
    with get_session() as db:
        model = db.query(PaymentChannelModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'支付渠道不存在(id={params.id})')

        exists_count = db.query(PaymentChannelModel).filter(or_(
            PaymentChannelModel.key == params.key,
            PaymentChannelModel.name == params.name
        ), PaymentChannelModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError('KEY或名称已存在')

        # model.key = params.key # 禁止修改 key, 防止缓存溢出
        # model.locked = params.locked.value # 禁止更新
        model.name = params.name
        model.icon = params.icon
        model.status = params.status.value

        # __dict__ 是直接引用模型字段，commit() 后会重置字段，data 也会被改变
        # 所以需要先复制一份数据再提交，避免 commit() 后被重置
        data = model.__dict__
        data.pop("_sa_instance_state")
        params = data.copy()

        db.commit()

        update_cache(params)

    return True


def delete_payment_channel(id: int) -> bool:
    with get_session() as db:
        model = db.query(PaymentChannelModel).filter_by(id=id).first()
        if model is None:
            raise ValueError(f'支付渠道不存在(id={id})')

        exists_count = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.channel_id == id).count()
        if exists_count > 0:
            raise ValueError(f'当前渠道下存在 {exists_count} 个支付配置')
        if model.locked == MysqlBoolType.YES.value:
            raise ValueError('禁止删除无法删除')

        db.delete(model)
        db.commit()

        params = model.__dict__
        params.pop('_sa_instance_state')
        update_cache(params, is_delete=True)

    return True


def update_cache(params: dict, is_delete: bool = False) -> None:
    '''注意：模型的 key 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出'''
    print(params)
    if isinstance(params["locked"], MysqlBoolType):
        params["locked"] = params["locked"].value
    if isinstance(params["status"], StatusType):
        params["status"] = params["status"].value
    if isinstance(params["created_at"], datetime):
        params["created_at"] = params["created_at"].isoformat()
    if isinstance(params["updated_at"], datetime):
        params["updated_at"] = params["updated_at"].isoformat()
    with get_redis() as redis:
        if is_delete == False:
            redis.hset(REDIS_PAYMENT_CHANNEL,
                       params["key"], json.dumps(params))
        else:
            redis.hdel(REDIS_PAYMENT_CHANNEL, params["key"])


def rebuild_cache() -> None:
    with get_session() as db:
        with get_redis() as redis:
            items = db.query(PaymentChannelModel).order_by(
                asc('asc_sort_order')).all()
            redis.delete(REDIS_PAYMENT_CHANNEL)
            for item in items:
                params = item.__dict__
                params.pop('_sa_instance_state')
                if isinstance(params["status"], StatusType):
                    params["status"] = params["status"].value
                if isinstance(params["created_at"], datetime):
                    params["created_at"] = params["created_at"].isoformat()
                if isinstance(params["updated_at"], datetime):
                    params["updated_at"] = params["updated_at"].isoformat()
                redis.hset(REDIS_PAYMENT_CHANNEL,
                           params["key"], json.dumps(params))
