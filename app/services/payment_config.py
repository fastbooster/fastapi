#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/10 00:18


import json
from datetime import datetime

from sqlalchemy.sql.expression import asc, desc

from app.constants.constants import REDIS_PAYMENT_CONFIG
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.payment_settings import PaymentChannelModel, PaymentConfigModel
from app.schemas.payment_config import PaymentConfigItem, PaymentConfigSearchQuery
from app.schemas.schemas import StatusType, MysqlBoolType


def get_payment_config(id: int) -> PaymentConfigModel | None:
    with get_session(read_only=True) as db:
        item = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.id == id).first()

    if item is not None:
        return item

    return None


def get_payment_config_list(params: PaymentConfigSearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
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
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add_payment_config(params: PaymentConfigItem) -> None:
    if params.channel_key == 'balance':
        raise ValueError('余额支付不支持添加支付配置')
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

    if isinstance(params.channel_id, int):
        channel = db.query(PaymentChannelModel).filter(
            PaymentChannelModel.id == params.channel_id).first()
        if channel is None:
            raise ValueError(f'支付渠道不存在(id={params.channel_id})')
        params.channel_key = channel.key
    else:
        raise ValueError(f'必须选择支付渠道')

    fields = params.model_dump()
    fields = {k: v for k, v in fields.items() if k not in ('id', 'created_at', 'updated_at')}
    fields['app_private_key'] = prepare_app_private_key(
        fields['app_private_key'])
    fields['status'] = params.status.value

    model = PaymentConfigModel()
    model.from_dict(fields)

    db.add(model)
    db.commit()

    params.id = model.id
    update_cache(params.model_dump())


def edit_payment_config(params: PaymentConfigItem) -> None:
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={params.id})')

        exists_count = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.appid == params.appid, PaymentConfigModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError(f'appid={params.appid} 已存在')

        if isinstance(params.locked, MysqlBoolType):
            params.locked = params.locked.value
        if isinstance(params.status, StatusType):
            params.status = params.status.value

        old_miniappid = None
        fields = params.model_dump()

        # 禁止修改 appid, 防止缓存溢出
        exclude_fields = ('id', 'channel_id', 'channel_key', 'appid', 'locked', 'created_at', 'updated_at')
        fields = {k: v for k, v in fields.items() if k not in exclude_fields}
        if model.miniappid:
            old_miniappid = model.miniappid
            fields.pop('miniappid')  # 禁止修改 miniappid, 防止缓存溢出
        fields['app_private_key'] = prepare_app_private_key(
            fields['app_private_key'])

        model.from_dict(fields)
        db.commit()

        params = params.model_dump()
        params['miniappid'] = old_miniappid
        update_cache(params)


def update_status(params: PaymentConfigItem) -> None:
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={params.id})')
        model.status = params.status.value
        params = model.to_dict()
        db.commit()
        update_cache(params)


def delete_payment_config(id: int) -> None:
    with get_session() as db:
        model = db.query(PaymentConfigModel).filter_by(id=id).first()
        if model is None:
            raise ValueError(f'支付配置不存在(id={id})')

        db.delete(model)
        db.commit()

        params = model.__dict__
        params.pop('_sa_instance_state')
        update_cache(params, is_delete=True)


def update_cache(params: dict, is_delete: bool = False) -> None:
    """注意：模型的 appid 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出"""
    if isinstance(params["status"], StatusType):
        params["status"] = params["status"].value
    if isinstance(params["created_at"], datetime):
        params["created_at"] = params["created_at"].isoformat()
    if isinstance(params["updated_at"], datetime):
        params["updated_at"] = params["updated_at"].isoformat()
    with get_redis() as redis:
        if not is_delete:
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
    with get_session(read_only=True) as db:
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


def prepare_app_private_key(private_key: str | None) -> str | None:
    """由于支付宝密钥工具生成的私钥为纯字符串，需要处理成 PEM 格式，添加头尾和换行, 结尾必须有一个换行符"""
    if private_key is None:
        return None
    if '\n' in private_key:
        return private_key

    private_key = '\n'.join([private_key[i:i + 64] for i in range(0, len(private_key), 64)])
    private_key = f'-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----\n'

    return private_key
