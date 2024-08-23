#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: FastBooster Generator
# Time: 2024-08-23 13:30

import json

from sqlalchemy.sql.expression import asc, desc

from app.constants.constants import REDIS_PAYMENT_CONFIG
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.payment_settings import PaymentConfigModel, PaymentChannelModel
from app.schemas.payment_config import PaymentConfigForm, PaymentConfigStatusForm, SearchQuery
from app.schemas.schemas import StatusType, MysqlBoolType
from app.utils.helper import serialize_datetime


def get(id: int) -> PaymentConfigModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(PaymentConfigModel).filter(PaymentConfigModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(PaymentConfigModel).order_by(desc('id'))
        if isinstance(params.channel_id, int):
            query = query.filter(PaymentConfigModel.channel_id == params.channel_id)
        if isinstance(params.status, StatusType):
            query = query.filter(PaymentConfigModel.status == params.status.value)
        if params.name:
            query = query.filter(PaymentConfigModel.name.like(f'%{params.name}%'))
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: PaymentConfigForm) -> None:
    if params.channel_key == 'balance':
        raise ValueError('余额支付不支持添加支付配置')
    with get_session() as db:
        exists_count = db.query(PaymentConfigModel.id).filter(PaymentConfigModel.appid == params.appid).count()
        if exists_count > 0:
            raise ValueError(f'appid={params.appid}已存在')
        if params.miniappid is not None:
            exists_count = db.query(PaymentConfigModel.id).filter(
                PaymentConfigModel.miniappid == params.miniappid).count()
            if exists_count > 0:
                raise ValueError(f'miniappid={params.miniappid}已存在')

        last_item = db.query(PaymentConfigModel).order_by(desc('id')).first()
        params.asc_sort_order = 1 if last_item is None or last_item.asc_sort_order is None else last_item.asc_sort_order + 1

        if isinstance(params.channel_id, int):
            channel = db.query(PaymentChannelModel).filter(PaymentChannelModel.id == params.channel_id).first()
            if channel is None:
                raise ValueError(f'支付渠道不存在(id={params.channel_id})')
            params.channel_key = channel.key
        else:
            raise ValueError(f'必须选择支付渠道')

        params.app_private_key = prepare_app_private_key(params.app_private_key)
        if isinstance(params.status, StatusType):
            params.status = params.status.value
        if isinstance(params.locked, MysqlBoolType):
            params.locked = params.locked.value

        current_model = PaymentConfigModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update(id: int, params: PaymentConfigForm) -> None:
    with get_session() as db:
        current_model = db.query(PaymentConfigModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'支付配置不存在(id={id})')

        params.app_private_key = prepare_app_private_key(params.app_private_key)
        if isinstance(params.status, StatusType):
            params.status = params.status.value
        if isinstance(params.locked, MysqlBoolType):
            params.locked = params.locked.value

        fields = params.model_dump()

        # 禁止修改 appid 防止缓存溢出
        exclude_fields = ('channel_id', 'channel_key', 'appid', 'locked')
        fields = {k: v for k, v in fields.items() if k not in exclude_fields}
        if current_model.miniappid:
            fields.pop('miniappid')  # 禁止修改 miniappid 防止缓存溢出

        current_model.from_dict(params.__dict__)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update_status(id: int, params: PaymentConfigStatusForm) -> None:
    with get_session() as db:
        current_model = db.query(PaymentConfigModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'支付配置不存在(id={id})')
        current_model.status = params.status.value
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(PaymentConfigModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'支付配置不存在(id={id})')
        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def update_cache(current_model: PaymentConfigModel, is_delete: bool = False) -> None:
    """注意：模型的 appid 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出"""
    with get_redis() as redis:
        if not is_delete:
            params = current_model.to_dict()
            params['created_at'] = serialize_datetime(params['created_at'])
            params['updated_at'] = serialize_datetime(params['updated_at'])
            cache_content = json.dumps(params)
            redis.hset(REDIS_PAYMENT_CONFIG, params["appid"], cache_content)
            # 兼容微信小程序支付, 小程序支付回调返回的 appid 是小程序的 appid, 而不是配置项里面的 appid
            # 所以在保存设置时，需要按 miniappid 保存一份
            if params["miniappid"] is not None:
                redis.hset(REDIS_PAYMENT_CONFIG, params["miniappid"], cache_content)
        else:
            redis.hdel(REDIS_PAYMENT_CONFIG, current_model.appid)


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        with get_redis() as redis:
            items = db.query(PaymentConfigModel).order_by(asc('asc_sort_order')).all()
            redis.delete(REDIS_PAYMENT_CONFIG)
            for item in items:
                update_cache(item)


def prepare_app_private_key(private_key: str | None) -> str | None:
    """由于支付宝密钥工具生成的私钥为纯字符串，需要处理成 PEM 格式，添加头尾和换行, 结尾必须有一个换行符"""
    if private_key is None:
        return None
    if '\n' in private_key:
        return private_key

    private_key = '\n'.join([private_key[i:i + 64] for i in range(0, len(private_key), 64)])
    private_key = f'-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----\n'

    return private_key
