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
from app.models.finance import BalanceModel, BalanceGiftModel, PointModel, ChenckinModel, PaymentAccountModel
from app.schemas.finance import SearchQuery, AdjustForm, CheckinType, PointType, PaymentAccountSearchQuery, \
    PaymentAccountFrontendSearchQuery, PaymentAccountAddForm, PaymentAccountEditForm
from app.tasks.finance import handle_balance, handle_balance_gift, handle_point
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
        if params.type > 0:
            query = query.filter_by(type=params.type)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def get_balance_gift_list(params: SearchQuery) -> list[BalanceGiftModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(BalanceGiftModel).order_by(desc('id'))
        if params.user_id > 0:
            query = query.filter_by(user_id=params.user_id)
        if params.type > 0:
            query = query.filter_by(type=params.type)
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
        if params.type > 0:
            query = query.filter_by(type=params.type)
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


def adjust_balance_gift(params: AdjustForm, user_data: dict) -> bool:
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
    result = handle_balance_gift.delay(data)
    logger.info(f'发送赠送余额动账任务:{result.id}', extra=data)

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


def get_payment_account_list(params: PaymentAccountSearchQuery) -> list[PaymentAccountModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(PaymentAccountModel).order_by(desc('id'))
        if params.id > 0:
            query = query.filter_by(id=params.id)
        if params.user_id > 0:
            query = query.filter_by(user_id=params.user_id)
        if params.type > 0:
            query = query.filter_by(type=params.type)
        if params.status > -1:
            query = query.filter_by(status=params.status)
        if params.account:
            query = query.filter(PaymentAccountModel.account.like(f'%{params.account}%'))
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def get_payment_account_list_frontend(params: PaymentAccountFrontendSearchQuery, user_id: int) -> list[dict]:
    with get_session() as db:
        query = db.query(
            PaymentAccountModel.id, PaymentAccountModel.user_id, PaymentAccountModel.type, PaymentAccountModel.account,
            PaymentAccountModel.status,
            PaymentAccountModel.user_memo, PaymentAccountModel.created_at
        ).order_by(desc(PaymentAccountModel.id))

        query = query.filter(PaymentAccountModel.user_id == user_id)
        if params.id > 0:
            query = query.filter_by(id=params.id)
        if params.type > 0:
            query = query.filter_by(type=params.type)
        if params.status > -1:
            query = query.filter_by(status=params.status)
        if params.account:
            query = query.filter(PaymentAccountModel.account.like(f'%{params.account}%'))

        results = query.all()

    list = [result._asdict() for result in results]
    return list


def add_payment_account(params: PaymentAccountAddForm, user_id: int) -> bool:
    with get_session() as db:
        exist_account = db.query(PaymentAccountModel).filter(PaymentAccountModel.type == params.type.value,
                                                             PaymentAccountModel.account == params.account).first()
        if exist_account is not None:
            raise ValueError(f'支付账号已存在(account={params.account})')

        payment_account_model = PaymentAccountModel(
            user_id=user_id,
            type=params.type.value,
            account=params.account,
            status=params.status,
            user_memo=params.user_memo,
        )

        db.add(payment_account_model)
        db.commit()

    return True


def edit_payment_account(params: PaymentAccountEditForm, user_id: int) -> bool:
    with get_session() as db:
        payment_account_model = db.query(PaymentAccountModel).filter(PaymentAccountModel.id == params.id,
                                                                     PaymentAccountModel.user_id == user_id).first()
        if payment_account_model is None:
            raise ValueError(f'支付账号不存在(id={params.id})')

        exist_account = db.query(PaymentAccountModel).filter(PaymentAccountModel.type == params.type.value,
                                                             PaymentAccountModel.account == params.account,
                                                             PaymentAccountModel.id != params.id).first()
        if exist_account is not None:
            raise ValueError(f'支付账号已存在(account={params.account})')

        payment_account_model.type = params.type.value
        payment_account_model.account = params.account
        payment_account_model.status = params.status
        payment_account_model.user_memo = params.user_memo

        db.commit()

    return True


def delete_payment_account(id: int, user_id: int) -> bool:
    with get_session() as db:
        payment_account_model = db.query(PaymentAccountModel).filter(PaymentAccountModel.id == id,
                                                                     PaymentAccountModel.user_id == user_id).first()
        if payment_account_model is None:
            raise ValueError(f'支付账号不存在(id={id})')

        db.delete(payment_account_model)
        db.commit()

    return True
