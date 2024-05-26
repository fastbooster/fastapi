#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 11:52

from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session
from app.core.log import logger
from app.models.finance import BalanceModel, PointModel
from app.schemas.finance import SearchQuery, AdjustForm
from app.tasks.finance import handle_balance, handle_point


def safe_whitelist_fields(post_data: dict) -> dict:
    safe_fields = ['id', 'type', 'amount', 'balance', 'auto_memo', 'back_memo', 'created_at']
    return {k: v for k, v in post_data.items() if k in safe_fields}


def get_balance_list(params: SearchQuery) -> list[BalanceModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(BalanceModel).order_by(desc('id'))
        if params.user_id > 0:
            query = query.filter_by(user_id=params.user_id)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def get_point_list(params: SearchQuery) -> list[PointModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(PointModel).order_by(desc('id'))
        if params.user_id > 0:
            query = query.filter_by(user_id=params.user_id)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def adjust_balance(params: AdjustForm, user_data: dict) -> bool:
    data = {
        'type': params.type.value,
        'user_id': params.user_id,
        'related_id': params.related_id,
        'amount': params.amount,
        'balance': 0,
        'auto_memo': params.auto_memo,
        'back_memo': f"{user_data['nickname']}({user_data['id']})",
        'ip': params.ip,
    }
    result = handle_balance.delay(data)
    logger.info(f'发送余额动账任务:{result.id}', extra=data)

    return True


def adjust_point(params: AdjustForm, user_data: dict) -> bool:
    data = {
        'type': params.type.value,
        'user_id': params.user_id,
        'related_id': params.related_id,
        'amount': params.amount,
        'balance': 0,
        'auto_memo': params.auto_memo,
        'back_memo': f"{user_data['nickname']}({user_data['id']})",
        'ip': params.ip,
    }
    result = handle_point.delay(data)
    logger.info(f'发送积分动账任务:{result.id}', extra=data)

    return True
