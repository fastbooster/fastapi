#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 11:52

import json
import uuid
import time

from sqlalchemy.sql.expression import desc
from datetime import datetime, timedelta
from typing import List
from urllib.parse import urlencode

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.core.log import logger
from app.models.finance import BalanceModel, BalanceGiftModel, PointModel, ChenckinModel, PaymentAccountModel, \
    PointRechargeModel, BalanceRechargeModel
from app.models.system_option import SystemOptionModel
from app.schemas.finance import SearchQuery, AdjustForm, CheckinType, PointType, PaymentAccountSearchQuery, \
    PaymentAccountFrontendSearchQuery, PaymentAccountAddForm, PaymentAccountEditForm, PointRechargeSettingForm, \
    BalanceRechargeSettingForm, PaymentStatuType, ScanpayForm, PaymentToolType
from app.tasks.finance import handle_balance, handle_balance_gift, handle_point
from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD
from app.services import system_option as SystemOptionService
from app.schemas.config import Settings
from app.core.payment import payment_manager


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


def get_point_recharge_setting() -> list:
    with get_redis() as redis:
        setting = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, 'point_recharge_setting')
        setting = json.loads(setting) if setting else []

    return setting


def get_balance_recharge_setting() -> list:
    with get_redis() as redis:
        setting = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, 'balance_recharge_setting')
        setting = json.loads(setting) if setting else []

    return setting


def update_point_recharge_settings(settings: List[PointRechargeSettingForm]) -> bool:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(option_name='point_recharge_setting').first()
        if option_model is None:
            option_model = SystemOptionModel(
                option_name='point_recharge_setting',
                option_value=json.dumps([setting.__dict__ for setting in settings]),
                richtext=0,
                position=0,
                autoload=1,
                lock=1,
                memo=None,
            )
            db.add(option_model)
        else:
            option_model.option_value = json.dumps([setting.__dict__ for setting in settings])

        db.commit()
        SystemOptionService.update_cache(option_model)

    return True


def update_balance_recharge_settings(settings: List[BalanceRechargeSettingForm]) -> bool:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(option_name='balance_recharge_setting').first()
        if option_model is None:
            option_model = SystemOptionModel(
                option_name='balance_recharge_setting',
                option_value=json.dumps([setting.__dict__ for setting in settings]),
                richtext=0,
                position=0,
                autoload=1,
                lock=1,
                memo=None,
            )
            db.add(option_model)
        else:
            option_model.option_value = json.dumps([setting.__dict__ for setting in settings])

        db.commit()
        SystemOptionService.update_cache(option_model)

    return True


def point_unifiedorder(sku_id: int, user_id: int, user_ip: str) -> dict:
    settings = Settings()
    if not settings.ENDPOINT.portal or not settings.ENDPOINT.pay or not settings.ENDPOINT.mp:
        raise ValueError('端点未配置')

    recharge_setting = get_point_recharge_setting()
    if not recharge_setting:
        raise ValueError('积分充值设置未配置')

    if sku_id < len(recharge_setting) and sku_id >= 0:
        sku = recharge_setting[sku_id]
        if not sku:
            raise ValueError('SKU不存在')
    else:
        raise ValueError('sku_id超出范围')

    trade_no = str(uuid.uuid4()).replace('-', '')
    with get_session() as db:
        order_model = PointRechargeModel(
            user_id=user_id,
            trade_no=trade_no,
            amount=sku['price'],
            points=sku['amount'],
            gift_points=sku['gift_amount'],
            user_ip=user_ip,
            auto_memo=json.dumps(sku, default=str),
        )
        db.add(order_model)

        db.commit()

    # 返回H5收银台地址, 由前端生成二维码, 用户扫码进入此页面进行支付
    params = {
        'order_type': 'point_recharge',
        'trade_no': trade_no,
    }

    return {
        'trade_no': trade_no,
        'url': f"{settings.ENDPOINT.mp.rstrip('/')}/checkout?{urlencode(params)}",
        'original_amount': sku['original_price'],
        'total_amount': sku['price'],
        'total_points': sku['amount'],
        'gift_points': sku['gift_amount'],
    }


def balance_unifiedorder(sku_id: int, user_id: int, user_ip: str) -> dict:
    settings = Settings()
    if not settings.ENDPOINT.portal or not settings.ENDPOINT.pay or not settings.ENDPOINT.mp:
        raise ValueError('端点未配置')

    recharge_setting = get_balance_recharge_setting()
    if not recharge_setting:
        raise ValueError('余额充值设置未配置')

    if sku_id < len(recharge_setting) and sku_id >= 0:
        sku = recharge_setting[sku_id]
        if not sku:
            raise ValueError('SKU不存在')
    else:
        raise ValueError('sku_id超出范围')

    trade_no = str(uuid.uuid4()).replace('-', '')
    with get_session() as db:
        order_model = BalanceRechargeModel(
            user_id=user_id,
            trade_no=trade_no,
            amount=sku['price'],
            gift_amount=sku['gift_amount'],
            user_ip=user_ip,
            auto_memo=json.dumps(sku, default=str),
        )
        db.add(order_model)

        db.commit()

    # 返回H5收银台地址, 由前端生成二维码, 用户扫码进入此页面进行支付
    params = {
        'order_type': 'balance_recharge',
        'trade_no': trade_no,
    }

    return {
        'trade_no': trade_no,
        'url': f"{settings.ENDPOINT.mp.rstrip('/')}/checkout?{urlencode(params)}",
        'original_amount': sku['original_price'],
        'total_amount': sku['price'],
        'gift_amount': sku['gift_amount'],
    }


def point_check(trade_no: str, user_id: int) -> dict:
    with get_session() as db:
        order_model = db.query(PointRechargeModel).filter_by(trade_no=trade_no).first()
        if order_model is None or order_model.user_id != user_id:
            raise ValueError('订单不存在')

    return {
        # 是否继续发起检测
        'continue': 1 if order_model.payment_status == PaymentStatuType.PAYMENT_STATUS_CREATED.value else 0,
        # 订单状态, 前端据此处理显示, 跳转等操作
        'status': order_model.payment_status,
    }


def balance_check(trade_no: str, user_id: int) -> dict:
    with get_session() as db:
        order_model = db.query(BalanceRechargeModel).filter_by(trade_no=trade_no).first()
        if order_model is None or order_model.user_id != user_id:
            raise ValueError('订单不存在')

    return {
        # 是否继续发起检测
        'continue': 1 if order_model.payment_status == PaymentStatuType.PAYMENT_STATUS_CREATED.value else 0,
        # 订单状态, 前端据此处理显示, 跳转等操作
        'status': order_model.payment_status,
    }


def point_scanpay(params: ScanpayForm, user_data: dict) -> dict:
    with get_session() as db:
        order_model = db.query(PointRechargeModel).filter_by(trade_no=params.trade_no).first()
        if order_model is None or order_model.user_id != user_data[
            'id'] or order_model.payment_status != PaymentStatuType.PAYMENT_STATUS_CREATED.value:
            raise ValueError('订单已失效, 请重新下单')

        amount = order_model.amount
        user_ip = order_model.user_ip
        # 更新订单创建时间, 防止被关单进程关闭此订单
        order_model.created_at = datetime.now()
        if params.openid is not None:
            order_model.back_memo = f'OPENID:{params.openid}'

        db.commit()

    settings = Settings()
    if params.client == 'wechat':
        openid = params.openid if params.openid and params.openid.lower() != 'none' else user_data['wechat_openid']
        if openid is None:
            raise ValueError('您的账号尚未绑定微信')
        wechatpy = payment_manager.get_instance('wechat')
        result = wechatpy.order.create(
            trade_type='JSAPI',
            body='积分充值',
            out_trade_no=params.trade_no,
            total_fee=int(amount * 100),
            spbill_create_ip=user_ip,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/portal/finance/wechat/point/notify",
            openid=openid,
        )
        if 'return_code' not in result or result['return_code'] != 'SUCCESS' or result['result_code'] != 'SUCCESS':
            error_msg = result.get('return_msg', '')
            error_code_des = result.get('err_code_des', '')
            raise ValueError(f"Get Wechat API Error: {error_msg}{error_code_des}", result, result.get('return_code'))

        if 'timestamp' not in result:
            result['timestamp'] = str(int(time.time()))
        return result
    else:
        alipay = payment_manager.get_instance('alipay')
        order_string = alipay.client_api(
            "alipay.trade.wap.pay",
            biz_content={
                "out_trade_no": params.trade_no,
                "total_amount": float(amount),
                "subject": "积分充值",
            },
            return_url=settings.ENDPOINT.portal,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/portal/finance/alipay/point/notify"
        )
        return {'url': f"{alipay._gateway}?{order_string}"}


def balance_scanpay(params: ScanpayForm, user_data: dict) -> dict:
    with get_session() as db:
        order_model = db.query(BalanceRechargeModel).filter_by(trade_no=params.trade_no).first()
        if order_model is None or order_model.user_id != user_data[
            'id'] or order_model.payment_status != PaymentStatuType.PAYMENT_STATUS_CREATED.value:
            raise ValueError('订单已失效, 请重新下单')

        amount = order_model.amount
        user_ip = order_model.user_ip

        # 更新订单创建时间, 防止被关单进程关闭此订单
        order_model.created_at = datetime.now()
        if params.openid is not None:
            order_model.back_memo = f'OPENID:{params.openid}'
        db.commit()

    settings = Settings()
    if params.client == 'wechat':
        openid = params.openid if params.openid and params.openid.lower() != 'none' else user_data['wechat_openid']
        if openid is None:
            raise ValueError('您的账号尚未绑定微信')
        wechatpy = payment_manager.get_instance('wechat')
        result = wechatpy.order.create(
            trade_type='JSAPI',
            body='余额充值',
            out_trade_no=params.trade_no,
            total_fee=int(amount * 100),
            spbill_create_ip=user_ip,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/portal/finance/wechat/balance/notify",
            openid=openid,
        )
        if 'return_code' not in result or result['return_code'] != 'SUCCESS' or result['result_code'] != 'SUCCESS':
            error_msg = result.get('return_msg', '')
            error_code_des = result.get('err_code_des', '')
            raise ValueError(f"Get Wechat API Error: {error_msg}{error_code_des}", result, result.get('return_code'))

        if 'timestamp' not in result:
            result['timestamp'] = str(int(time.time()))
        return result
    else:
        alipay = payment_manager.get_instance('alipay')
        order_string = alipay.client_api(
            "alipay.trade.wap.pay",
            biz_content={
                "out_trade_no": params.trade_no,
                "total_amount": float(amount),
                "subject": "余额充值",
            },
            return_url=settings.ENDPOINT.portal,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/portal/finance/alipay/balance/notify"
        )
        return {'url': f"{alipay._gateway}?{order_string}"}


def point_notify(payment_tool: str, params: dict, content: str = None) -> bool:
    logger.info(f'收到异步通知:{payment_tool}', extra=params)
    if payment_tool == PaymentToolType.PAYMENT_TOOL_ALIPAY.value:
        signature = params.pop('sign')
        alipay = payment_manager.get_instance('alipay', params.get('app_id', None))
        try:
            success = alipay.verify(params, signature)
        except:
            logger.error(f'签名验证失败:{payment_tool}', extra=params)
            return False
        if not success:
            logger.error(f'签名验证失败:{payment_tool}', extra=params)
            return False
        is_ok = True if params["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED") else False
    elif payment_tool == PaymentToolType.PAYMENT_TOOL_WECHAT.value:
        # 如果是小程序支付, appid返回的是小程序的appid, 不是支付配置里面的appid
        wechatpy = payment_manager.get_instance('wechat', params.get('mch_id', None))
        try:
            params = wechatpy.parse_payment_result(content)
        except:
            logger.error(f'签名验证失败:{payment_tool}', extra=params)
            return False
        is_ok = False if params["return_code"] == "SUCCESS" and params["refund_status"] == "SUCCESS" else False
    else:
        return False

    # 订单处理
    with get_session() as db:
        order_model = db.query(PointRechargeModel).filter_by(trade_no=params.get('out_trade_no')).first()
        if order_model is None:
            logger.info('订单不存在', extra=params)
            return False
        if order_model.payment_status not in (
        PaymentStatuType.PAYMENT_STATUS_CREATED.value, PaymentStatuType.PAYMENT_STATUS_CLOSE.value):
            logger.info(f'订单状态异常:{order_model.payment_status}', extra=params)
            return True

        order_model.payment_status = PaymentStatuType.PAYMENT_STATUS_SUCCESS.value if is_ok else PaymentStatuType.PAYMENT_STATUS_FAIL.value
        order_model.payment_tool = payment_tool
        order_model.payment_time = datetime.now()
        order_model.payment_response = json.dumps(params, default=str)

        # 积分变动
        if is_ok:
            task_data = {
                'type': PointType.TYPE_RECHARGE.value,
                'user_id': order_model.user_id,
                'related_id': order_model.id,
                'amount': order_model.points,
                'balance': 0,
                'auto_memo': '用户充值',
                'back_memo': None,
                'ip': order_model.user_ip,
            }
            task_result = handle_point.delay(task_data)
            logger.info(f'发送积分动账任务:{task_result.id}', extra=task_data)

            if order_model.gift_points > 0:
                task_gift_data = {
                    'type': PointType.TYPE_RECHARGE_GIFT.value,
                    'user_id': order_model.user_id,
                    'related_id': order_model.id,
                    'amount': order_model.gift_points,
                    'balance': 0,
                    'auto_memo': '用户充值赠送',
                    'back_memo': None,
                    'ip': order_model.user_ip,
                }
                task_gift_result = handle_point.delay(task_gift_data)
                logger.info(f'发送积分动账任务:{task_gift_result.id}', extra=task_gift_data)

            logger.info('成功受理通知', extra=params)

        db.commit()

        return is_ok
