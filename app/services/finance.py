#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 11:52

from sqlalchemy.sql.expression import desc
from datetime import datetime, timedelta

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.core.log import logger
from app.models.finance import BalanceModel, PointModel, ChenckinModel
from app.schemas.finance import SearchQuery, AdjustForm, CheckinType, PointType
from app.tasks.finance import handle_balance, handle_point
from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD


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


def checkin(user_id: int, ip: str, user_agent: str) -> bool:
    # 获取当前日期
    today = datetime.now().date()

    with get_session() as db:
        # 查询用户的最近签到记录
        latest_checkin = db.query(ChenckinModel).filter_by(user_id=user_id).order_by(
            ChenckinModel.created_at.desc()).first()

        # 检查最近签到记录是否存在
        if latest_checkin is not None:
            # 获取最近签到日期
            latest_checkin_date = latest_checkin.created_at.date()
            total_days = latest_checkin.total_days + 1

            # 检查最近签到日期是否是昨天
            if latest_checkin_date == today - timedelta(days=1):
                # 连续签到
                keep_days = latest_checkin.keep_days + 1
            elif latest_checkin_date == today:
                # 今天已经签到过了
                raise ValueError('今天已经签到')
            else:
                # 断签，重新开始计数
                keep_days = 1
        else:
            # 用户没有签到过
            keep_days = 1
            total_days = 1

        # 创建签到记录
        with get_redis() as redis:
            points = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, 'checkin_point')
        points = int(points) if points else 1
        checkin = ChenckinModel(user_id=user_id, type=CheckinType.TYPE_CHECKIN.value, total_days=total_days,
                                keep_days=keep_days, points=points, ip=ip, user_agent=user_agent)
        db.add(checkin)
        db.commit()

        # 新增积分
        data = {
            'type': PointType.TYPE_CHECKIN.value,
            'user_id': user_id,
            'related_id': checkin.id,
            'amount': points,
            'balance': 0,
            'auto_memo': f"{today}签到",
            'ip': ip,
        }
        result = handle_point.delay(data)
        logger.info(f'发送积分动账任务:{result.id}', extra=data)

    return True
