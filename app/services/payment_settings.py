#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/11 10:35


from typing import List

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session

from app.models.payment_settings import PaymentChannelModel, PaymentConfigModel
from app.schemas.schemas import StatusType
from app.schemas.payment_settings import PaymentSettingsSortForm, PaymentSettingItem, PaymentSettingListResponse


def get_payment_settings(status: StatusType = None) -> PaymentSettingListResponse | None:
    items = []
    with get_session() as db:
        query = db.query(PaymentChannelModel).order_by(asc('asc_sort_order'))
        if isinstance(status, StatusType):
            query = query.filter(PaymentChannelModel.status == status.value)

        channels = query.all()
        if (len(channels) == 0):
            return None

        for channel in channels:
            item = PaymentSettingItem(channel=channel.__dict__, children=[])

            query = db.query(PaymentConfigModel).order_by(
                asc('asc_sort_order'))
            query = query.filter(PaymentConfigModel.channel_id == channel.id)
            if isinstance(status, StatusType):
                query = query.filter(PaymentConfigModel.status == status.value)

            item.children = query.all()
            items.append(item)

    return PaymentSettingListResponse(total=len(items), items=items)


def update_sort(params: PaymentSettingsSortForm) -> None:
    with get_session() as db:
        channels = db.query(PaymentChannelModel).all()
        configs = db.query(PaymentConfigModel).all()

        for channel in channels:
            channel.asc_sort_order = params.channel_ids.index(channel.id)
        for config in configs:
            config.asc_sort_order = params.config_ids.index(config.id)

        db.commit()
