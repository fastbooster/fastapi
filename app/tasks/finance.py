#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/24 16:43

from app.core.single_celery import app_single
from app.core.mysql import get_session
from app.schemas.finance import BalanceType, PointType
from app.models.finance import BalanceModel, BalanceGiftModel, PointModel
from app.core.log import logger


# 余额处理任务
@app_single.task
def handle_balance(data: dict):
    task_id = handle_balance.request.id
    try:
        with get_session() as db:
            if data['type'] == BalanceType.RECHARGE.value:
                result = db.query(BalanceModel).filter(BalanceModel.user_id == data['user_id'],
                                                       BalanceModel.related_id == data['related_id']).first()
                if result:
                    logger.info(f'当前余额动账({task_id})已处理过, 本次忽略', extra=data)
                    return

            # 余额动账
            last = db.query(BalanceModel).filter(BalanceModel.user_id == data['user_id']).order_by(
                BalanceModel.id.desc()).first()
            balance = last.balance if last is not None else 0
            data['balance'] = balance + data['amount']

            db.add(BalanceModel(**data))
            db.commit()
            logger.info(f'余额动账成功({task_id})', extra=data)
    except Exception as e:
        # 处理异常情况
        logger.error(f'消费余额动账({task_id})失败：{e}', extra=data)
        raise
    finally:
        pass


# 赠送余额处理任务
@app_single.task
def handle_balance_gift(data: dict):
    task_id = handle_balance.request.id
    try:
        with get_session() as db:
            if data['type'] == BalanceType.GIFT.value:
                result = db.query(BalanceGiftModel).filter(BalanceGiftModel.user_id == data['user_id'],
                                                           BalanceGiftModel.related_id == data['related_id']).first()
                if result:
                    logger.info(f'当前赠送余额动账({task_id})已处理过, 本次忽略', extra=data)
                    return

            # 赠送余额动账
            last = db.query(BalanceGiftModel).filter(BalanceGiftModel.user_id == data['user_id']).order_by(
                BalanceGiftModel.id.desc()).first()
            balance = last.balance if last is not None else 0
            data['balance'] = balance + data['amount']

            db.add(BalanceGiftModel(**data))
            db.commit()
            logger.info(f'赠送余额动账成功({task_id})', extra=data)
    except Exception as e:
        # 处理异常情况
        logger.error(f'消费赠送余额动账({task_id})失败：{e}', extra=data)
        raise
    finally:
        pass


# 积分处理任务
@app_single.task
def handle_point(data: dict):
    task_id = handle_point.request.id
    try:
        with get_session() as db:
            if data['type'] == PointType.RECHARGE.value:
                result = db.query(PointModel).filter(PointModel.user_id == data['user_id'],
                                                     PointModel.related_id == data['related_id']).first()
                if result:
                    logger.info(f'当前积分动账({task_id})已处理过, 本次忽略', extra=data)
                    return

            # 积分动账
            last = db.query(PointModel).filter(PointModel.user_id == data['user_id']).order_by(
                PointModel.id.desc()).first()
            balance = last.balance if last is not None else 0
            data['balance'] = balance + data['amount']

            db.add(PointModel(**data))
            db.commit()
            logger.info(f'积分动账成功({task_id})', extra=data)
    except Exception as e:
        # 处理异常情况
        logger.error(f'消费积分动账({task_id})失败：{e}', extra=data)
        raise
    finally:
        pass
