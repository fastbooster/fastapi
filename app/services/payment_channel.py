#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 11:01


from sqlalchemy import or_
from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session

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

        model.key = params.key
        model.name = params.name
        model.icon = params.icon
        # model.locked = params.locked.value # 禁止更新
        model.status = params.status.value

        db.commit()

    return True


def delete_payment_channel(id: int) -> bool:
    with get_session() as db:
        model = db.query(PaymentChannelModel).filter_by(id=id).first()
        if model is None:
            raise ValueError(f'支付渠道不存在(id={id})')

        exists_count = db.query(PaymentConfigModel).filter(
            PaymentConfigModel.channel_id != id).count()
        if exists_count > 0:
            raise ValueError(f'当前渠道下存在 {exists_count} 个支付配置')
        if model.locked == MysqlBoolType.YES.value:
            raise ValueError('禁止删除无法删除')

        db.delete(model)
        db.commit()

    return True
