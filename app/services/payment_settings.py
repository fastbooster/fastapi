#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/11 10:35

import json
from typing import List

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session
from app.core.redis import get_redis

from app.models.payment_settings import PaymentChannelModel, PaymentConfigModel
from app.schemas.schemas import StatusType
from app.schemas.payment_settings import PaymentSettingsSortForm, PaymentSettingItem, PaymentSettingListResponse, PaymentSettingOutItem, PaymentSettingOutListResponse
from app.schemas.payment_channel import PaymentChannelOutItem
from app.schemas.payment_config import PaymentConfigOutItem

from app.services import payment_config as PaymentConfigService, payment_channel as PaymentChannelService

from app.constants.constants import REDIS_PAYMENT_CHANNEL, REDIS_PAYMENT_CONFIG


def get_payment_settings_from_cache() -> PaymentSettingOutListResponse:
    with get_redis() as redis:
        channels = redis.hgetall(REDIS_PAYMENT_CHANNEL)
        channels = [json.loads(channels[key]) for key in channels]
        channels.sort(key=lambda x: int(x["asc_sort_order"]))

        configs = redis.hgetall(REDIS_PAYMENT_CONFIG)
        configs = [json.loads(configs[key]) for key in configs]
        configs.sort(key=lambda x: int(x["asc_sort_order"]))

        # 由于微信支付会根据 miniappid 多存一份缓存，所以这里需要去重
        items = []
        exists_config_ids = []
        for channel in channels:
            item = {"channel": PaymentChannelOutItem(
                **channel), "children": []}
            for config in configs:
                if config["id"] not in exists_config_ids and config["channel_id"] == channel["id"]:
                    exists_config_ids.append(config["id"])
                    item["children"].append(PaymentConfigOutItem(**config))

            items.append(item)

        return PaymentSettingOutListResponse(total=len(items), items=items)


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

        PaymentConfigService.rebuild_cache()
        PaymentChannelService.rebuild_cache()
