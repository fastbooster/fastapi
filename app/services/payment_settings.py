#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/11 10:35

import json

from sqlalchemy.sql.expression import asc

from app.constants.constants import REDIS_PAYMENT_CHANNEL, REDIS_PAYMENT_CONFIG
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.payment_settings import PaymentChannelModel, PaymentConfigModel
from app.schemas.payment_channel import PaymentChannelPublicItem
from app.schemas.payment_config import PaymentConfigPublicItem
from app.schemas.payment_settings import PaymentSettingsSortForm, PaymentSettingItem, PaymentSettingListResponse, \
    PaymentSettingOutListResponse
from app.schemas.schemas import StatusType
from app.services import payment_config, payment_channel


def get_payment_settings_from_cache() -> PaymentSettingOutListResponse:
    with get_redis() as redis:
        channels = redis.hgetall(REDIS_PAYMENT_CHANNEL)
        channels = [json.loads(channels[key]) for key in channels]
        channels.sort(key=lambda x: int(x["asc_sort_order"]))

        configs = redis.hgetall(REDIS_PAYMENT_CONFIG)
        configs = [json.loads(configs[key]) for key in configs]
        configs.sort(key=lambda x: int(x["asc_sort_order"]))

        # 过滤数据
        # 1. 由于微信支付会根据 miniappid 多存一份缓存，所以这里需要去重
        # 2. 已禁用的渠道和配置，需要过滤掉，因为这是列表给前端用户下单选择支付方式使用的数据
        # 3. 移除 children 为空的渠道
        items = []
        exists_config_ids = []
        for channel in channels:
            if channel["status"] != StatusType.ENABLED.value:
                continue
            item = {"channel": PaymentChannelPublicItem(
                **channel), "children": []}
            for config in configs:
                if config["status"] != StatusType.ENABLED.value:
                    continue
                if config["id"] not in exists_config_ids and config["channel_id"] == channel["id"]:
                    exists_config_ids.append(config["id"])
                    item["children"].append(PaymentConfigPublicItem(**config))
            if len(item["children"]) == 0:
                continue
            items.append(item)

        return PaymentSettingOutListResponse(total=len(items), items=items)


def get_payment_settings(status: StatusType = None) -> PaymentSettingListResponse | None:
    with get_session(read_only=True) as db:
        items = []
        query = db.query(PaymentChannelModel).order_by(asc('asc_sort_order'))
        if isinstance(status, StatusType):
            query = query.filter(PaymentChannelModel.status == status.value)

        channels = query.all()
        if len(channels) == 0:
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

        payment_config.rebuild_cache()
        payment_channel.rebuild_cache()
