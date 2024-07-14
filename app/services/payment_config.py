#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/10 00:18


import json

from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.core.redis import get_redis

from app.constants.constants import REDIS_PAYMENT_CONFIG

from app.models.payment_settings import PaymentConfigModel
from app.schemas.schemas import StatusType
from app.schemas.payment_config import PaymentConfigItem, PaymentConfigSearchQuery, PaymentConfigListResponse


def get_payment_config(id: int) -> PaymentConfigModel | None:
    with get_session() as db:
        item = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.id == id).first()

    if item is not None:
        return item

    return None


def get_payment_config_list(params: PaymentConfigSearchQuery) -> PaymentConfigListResponse:
    total = -1
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(PaymentConfigModel).order_by(asc('asc_sort_order'))
        if isinstance(params.channel_id, int):
            query = query.filter(
                PaymentConfigModel.channel_id == params.channel_id)
        if params.name:
            query = query.filter(
                PaymentConfigModel.name.like(f'%{params.name}%'))
        if isinstance(params.status, StatusType):
            query = query.filter(
                PaymentConfigModel.status == params.status.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return {"total": total, "items": query.all()}


def add_payment_config(params: PaymentConfigItem) -> bool:
    with get_session() as db:
        exists_count = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.appid == params.appid).count()
        if exists_count > 0:
            raise ValueError(f'appid={params.appid}已存在')

        if params.miniappid is not None:
            exists_count = db.query(PaymentConfigModel).filter(
                PaymentConfigModel.miniappid == params.miniappid).count()
            if exists_count > 0:
                raise ValueError(f'miniappid={params.miniappid}已存在')

        last_item = db.query(PaymentConfigModel).order_by(desc('id')).first()
        params.asc_sort_order = 1 if last_item is None or last_item.asc_sort_order is None else last_item.asc_sort_order + 1

        fields = params.model_dump()
        fields.pop('id')
        fields.pop('created_at')
        fields.pop('updated_at')
        fields['status'] = params.status.value

        model = PaymentConfigModel(**fields)

        db.add(model)
        db.commit()

        params.id = model.id
        update_cache(params.model_dump())
    return True


def edit_payment_config(params: PaymentConfigItem) -> bool:
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={params.id})')

        exists_count = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.appid == params.appid, PaymentConfigModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError(f'appid={params.appid} 已存在')

        old_miniappid = None
        fields = params.model_dump()
        fields.pop('id')
        fields.pop('channel_id')
        fields.pop('appid')  # 禁止修改 appid, 防止缓存溢出
        if model.miniappid:
            old_miniappid = model.miniappid
            fields.pop('miniappid')  # 禁止修改 miniappid, 防止缓存溢出
        fields.pop('created_at')
        fields.pop('updated_at')
        fields['status'] = params.status.value

        model.from_dict(fields)
        db.commit()

        params = params.model_dump()
        params["miniappid"] = old_miniappid
        update_cache(params)

    return True


def update_status(params: PaymentConfigItem) -> bool:
    '''此操作无需更新缓存，因为状态变更后不会影响支付'''
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={params.id})')

        model.status = params.status.value

        db.commit()

    return True


def delete_payment_config(id: int) -> bool:
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(id=id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={id})')

        db.delete(model)
        db.commit()

        params = model.__dict__
        params.pop('_sa_instance_state')
        update_cache(params, is_delete=True)

    return True


def update_cache(params: dict, is_delete: bool = False) -> None:
    '''注意：模型的 appid 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出'''
    if isinstance(params["status"], StatusType):
        params["status"] = params["status"].value
    if isinstance(params["created_at"], datetime):
        params["created_at"] = params["created_at"].isoformat()
    if isinstance(params["updated_at"], datetime):
        params["updated_at"] = params["updated_at"].isoformat()
    with get_redis() as redis:
        if is_delete == False:
            redis.hset(REDIS_PAYMENT_CONFIG,
                       params["appid"], json.dumps(params))
            # 兼容微信小程序支付, 小程序支付回调返回的 appid 是小程序的 appid, 而不是配置项里面的 appid
            # 所以在保存设置时，需要按 miniappid 保存一份
            if params["miniappid"] is not None:
                redis.hset(REDIS_PAYMENT_CONFIG,
                           params["miniappid"], json.dumps(params))
        else:
            redis.hdel(REDIS_PAYMENT_CONFIG, params["appid"])


def rebuild_cache() -> None:
    with get_session() as db:
        with get_redis() as redis:
            items = db.query(PaymentConfigModel).order_by(
                asc('asc_sort_order')).all()
            redis.delete(REDIS_PAYMENT_CONFIG)
            for item in items:
                params = item.__dict__
                params.pop('_sa_instance_state')
                if isinstance(params["status"], StatusType):
                    params["status"] = params["status"].value
                if isinstance(params["created_at"], datetime):
                    params["created_at"] = params["created_at"].isoformat()
                if isinstance(params["updated_at"], datetime):
                    params["updated_at"] = params["updated_at"].isoformat()
                redis.hset(REDIS_PAYMENT_CONFIG,
                           params["appid"], json.dumps(params))
                if params["miniappid"] is not None:
                    redis.hset(REDIS_PAYMENT_CONFIG,
                               params["miniappid"], json.dumps(params))
