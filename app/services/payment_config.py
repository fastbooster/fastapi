#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/10 00:18


from sqlalchemy import or_
from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session

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
            raise ValueError(f'appid={params.appid} 已存在')

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

        fields = params.model_dump()
        fields.pop('id')
        fields.pop('channel_id')
        fields.pop('created_at')
        fields.pop('updated_at')
        fields['status'] = params.status.value

        model.from_dict(fields)

        db.commit()

    return True


def update_status(params: PaymentConfigItem) -> bool:
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

    return True
