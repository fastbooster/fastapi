#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: FastBooster Generator
# Time: 2024-08-23 22:09


import json
import time
import uuid
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

from sqlalchemy.sql.expression import desc, text

from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD
from app.core.log import logger
from app.core.mysql import get_session
from app.core.payment import payment_manager
from app.core.redis import get_redis
from app.models.finance import BalanceModel, BalanceGiftModel, BalanceRechargeModel
from app.schemas.balance_recharge import BalanceRechargeForm
from app.schemas.balance_recharge import SearchQuery
from app.schemas.config import Settings
from app.schemas.finance import BalanceType, PaymentStatusType, RechargeForm, PayForm, PaymentChannelType
from app.schemas.schemas import ClientType
from app.tasks.finance import handle_balance, handle_balance_gift


def get(id: Optional[int] = 0, trade_no: Optional[str] = None) -> BalanceRechargeModel | None:
    with get_session(read_only=True) as db:
        if id > 0:
            return db.query(BalanceRechargeModel).filter(BalanceRechargeModel.id == id).first()
        elif trade_no is not None:
            return db.query(BalanceRechargeModel).filter(BalanceRechargeModel.trade_no == trade_no).first()
        else:
            raise ValueError('id 和 trade_no 至少传入一项')


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(BalanceRechargeModel).order_by(desc('id'))
        if params.user_id:
            query = query.filter(
                BalanceRechargeModel.user_id == params.user_id)
        if params.trade_no:
            query = query.filter(
                BalanceRechargeModel.trade_no.like(f'%{params.trade_no}%'))
        if isinstance(params.payment_status, PaymentStatusType):
            query = query.filter(
                BalanceRechargeModel.payment_status == params.payment_status.value)
        if isinstance(params.payment_channel, PaymentChannelType):
            query = query.filter(
                BalanceRechargeModel.payment_channel == params.payment_channel.value)
        if isinstance(params.created_start, datetime):
            query = query.filter(
                BalanceRechargeModel.created_at >= params.created_start)
        if isinstance(params.created_end, datetime):
            query = query.filter(
                BalanceRechargeModel.created_at <= params.created_end)
        if isinstance(params.payment_start, datetime):
            query = query.filter(
                BalanceRechargeModel.payment_time >= params.payment_start)
        if isinstance(params.payment_end, datetime):
            query = query.filter(
                BalanceRechargeModel.payment_time <= params.payment_end)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: BalanceRechargeForm) -> None:
    with get_session() as db:
        if isinstance(params.payment_status, PaymentStatusType):
            params.payment_status = params.payment_status.value
        if isinstance(params.payment_channel, PaymentChannelType):
            params.payment_channel = params.payment_channel.value
        current_model = BalanceRechargeModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()


def update(id: int, params: BalanceRechargeForm) -> None:
    with get_session() as db:
        current_model = db.query(BalanceRechargeModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'余额充值日志不存在(id={id})')
        if isinstance(params.payment_status, PaymentStatusType):
            params.payment_status = params.payment_status.value
        if isinstance(params.payment_channel, PaymentChannelType):
            params.payment_channel = params.payment_channel.value
        current_model.from_dict(params.__dict__)
        db.commit()


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(BalanceRechargeModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'余额充值日志不存在(id={id})')
        db.delete(current_model)
        db.commit()


def get_recharge_settings() -> list:
    with get_redis() as redis:
        setting = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, 'balance_recharge_settings')
        setting = json.loads(setting) if setting else []
        return setting


def check_order(trade_no: str, user_id: int) -> BalanceRechargeModel:
    with get_session(read_only=True) as db:
        current_model = db.query(BalanceRechargeModel).filter_by(trade_no=trade_no).first()
        if current_model is None or current_model.user_id != user_id:
            raise ValueError('订单不存在')
    return current_model


def unifiedorder(params: RechargeForm, user_id: int, user_ip: str) -> dict:
    settings = Settings()
    if not settings.ENDPOINT.portal or not settings.ENDPOINT.pay or not settings.ENDPOINT.mp:
        raise ValueError('端点未配置')

    recharge_settings = get_recharge_settings()
    if not recharge_settings:
        raise ValueError('余额充值设置未配置')

    if len(recharge_settings) > params.sku_id >= 0:
        sku = recharge_settings[params.sku_id]
        if not sku:
            raise ValueError('SKU不存在')
    else:
        raise ValueError('sku_id超出范围')

    if sku['status'] != 1:
        raise ValueError('当前充值套餐已停用')

    # 自定义充值时计算可以获得的充值余额
    if sku["exchange_rate"] is not None:
        sku['price'] = params.price
        sku['origin_price'] = params.price
        sku['amount'] = params.price * sku["exchange_rate"]

    trade_no = str(uuid.uuid4()).replace('-', '')
    with get_session() as db:
        new_order = BalanceRechargeModel()
        new_order.from_dict({
            'user_id': user_id,
            'trade_no': trade_no,
            'amount': sku['amount'],
            'price': sku['price'],
            'gift_amount': sku['gift_amount'],
            'auto_memo': json.dumps(sku, default=str),
            'user_ip': user_ip,
        })
        db.add(new_order)
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


def pay(params: PayForm, user_data: dict) -> dict:
    """TODO: 定义返回数据模型"""
    with get_session() as db:
        order_model = db.query(BalanceRechargeModel).filter_by(trade_no=params.trade_no).first()
        if order_model is None or order_model.user_id != user_data[
            'id'] or order_model.payment_status != PaymentStatusType.CREATED.value:
            raise ValueError('订单已失效, 请重新下单')

        price = order_model.price
        user_ip = order_model.user_ip

        # 更新订单创建时间, 防止被关单进程关闭此订单, 非抢购，无需此操作
        # order_model.created_at = datetime.now()

        if params.openid is not None:
            order_model.back_memo = f'OPENID:{params.openid}'
        db.commit()

    settings = Settings()
    if params.channel == 'wechatpay':
        # TODO: 待测试
        openid = params.openid if params.openid and params.openid.lower(
        ) != 'none' else user_data['wechat_openid']
        if openid is None:
            raise ValueError('您的账号尚未绑定微信')
        wechatpy = payment_manager.get_instance('wechat')
        result = wechatpy.order.create(
            trade_type='JSAPI',
            body='余额充值',
            out_trade_no=params.trade_no,
            total_fee=int(price * 100),
            spbill_create_ip=user_ip,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/api/v1/frontend/balance_recharges/wechat/notify",
            openid=openid,
        )
        if 'return_code' not in result or result['return_code'] != 'SUCCESS' or result['result_code'] != 'SUCCESS':
            error_msg = result.get('return_msg', '')
            error_code_des = result.get('err_code_des', '')
            raise ValueError(f"Get Wechat API Error: {error_msg}{error_code_des}", result, result.get('return_code'))
        if 'timestamp' not in result:
            result['timestamp'] = str(int(time.time()))
        return result

    if params.channel == 'alipay':
        match params.client:
            case ClientType.PC_BROWSER:
                api_name = 'alipay.trade.page.pay'
                return_url = settings.ENDPOINT.portal
            case ClientType.MOBILE_BROWSER | ClientType.ALIPAY_BROWSER | ClientType.WECHAT_BROWSER:
                api_name = 'alipay.trade.wap.pay'
                return_url = settings.ENDPOINT.mp
            case ClientType.ANDROID_APP | ClientType.IOS_APP:
                # api_name = 'alipay.trade.app.pay'
                # product_code = 'QUICK_MSECURITY_PAY'
                raise ValueError('尚未支持APP客户端支付')
            case (_):
                raise ValueError('不支持的客户端类型')

        product_code = 'FAST_INSTANT_TRADE_PAY'
        alipay = payment_manager.get_instance('alipay', params.appid)
        order_string = alipay.client_api(
            api_name,
            biz_content={
                "out_trade_no": params.trade_no,
                "total_amount": float(price),
                "subject": "余额充值",
                "product_code": product_code,
            },
            return_url=return_url,
            notify_url=f"{settings.ENDPOINT.pay.rstrip('/')}/api/v1/frontend/balance_recharges/alipay/notify"
        )
        return {'url': f"{alipay._gateway}?{order_string}"}


def notify(payment_channel: str, params: dict, content: str = None) -> bool:
    """TODO: 1. 赠送余额入账"""
    logger.info(f'收到异步通知: {payment_channel}', extra=params)
    if payment_channel == PaymentChannelType.ALIPAY.value:
        signature = params.pop('sign')
        appid = params.get('app_id', None)
        alipay = payment_manager.get_instance('alipay', appid=appid)
        try:
            success = alipay.verify(params, signature)
        except:
            logger.error(f'签名验证失败: {payment_channel}', extra=params)
            return False
        if not success:
            logger.error(f'签名验证失败: {payment_channel}', extra=params)
            return False
        is_ok = True if params["trade_status"] in (
            "TRADE_SUCCESS", "TRADE_FINISHED") else False
    elif payment_channel == PaymentChannelType.WECHATPAY.value:
        # 如果是微信小程序支付, appid 返回的是小程序的 appid, 由于已经做了缓存适配，可以直接使用 appid 参数
        appid = params.get('appid', None)
        wechatpy = payment_manager.get_instance('wechat', appid=appid)
        try:
            params = wechatpy.parse_payment_result(content)
        except:
            logger.error(f'签名验证失败: {payment_channel}', extra=params)
            return False
        is_ok = False if params["return_code"] == "SUCCESS" and params["refund_status"] == "SUCCESS" else False
    else:
        return False

    # 订单处理
    with get_session() as db:
        order_model = db.query(BalanceRechargeModel).filter_by(
            trade_no=params.get('out_trade_no')).first()
        if order_model is None:
            logger.info('订单不存在', extra=params)
            return False
        if order_model.payment_status not in (
                PaymentStatusType.CREATED.value, PaymentStatusType.CLOSE.value):
            logger.info(f'订单状态异常: payment_status={
            order_model.payment_status}, 不接受异步通知', extra=params)
            return True

        order_model.payment_appid = appid
        order_model.payment_status = PaymentStatusType.SUCCESS.value if is_ok else PaymentStatusType.FAIL.value
        order_model.payment_channel = payment_channel
        order_model.payment_time = datetime.now()
        order_model.payment_response = json.dumps(params)

        # 余额变动
        if is_ok:
            task_data = {
                'type': BalanceType.RECHARGE.value,
                'user_id': order_model.user_id,
                'related_id': order_model.id,
                'amount': order_model.amount,
                'balance': 0,
                'auto_memo': '用户充值',
                'back_memo': None,
                'ip': order_model.user_ip,
            }
            task_result = handle_balance.delay(task_data)
            logger.info(f'发送余额动账任务: {task_result.id}', extra=task_data)

            if order_model.gift_amount > 0:
                task_gift_data = {
                    'type': BalanceType.GIFT.value,
                    'user_id': order_model.user_id,
                    'related_id': order_model.id,
                    'amount': order_model.gift_amount,
                    'balance': 0,
                    'auto_memo': '用户充值赠送',
                    'back_memo': None,
                    'ip': order_model.user_ip,
                }
                task_gift_result = handle_balance_gift.delay(task_gift_data)
                logger.info(
                    f'发送余额动账任务: {task_gift_result.id}', extra=task_gift_data)

            logger.info('成功受理通知', extra=params)

        db.commit()

        return is_ok


def refund(trade_no: str) -> None:
    """
    ### 注意：
    1. 只支持全额退款
    2. 余额和赠送余额同时全额退款，有任何一个余额不足都不能退款
    3. TODO: 定义更多入参，memo, ip 等"""
    with get_session() as db:
        order = db.query(BalanceRechargeModel).filter_by(
            trade_no=trade_no).first()
        if order is None:
            raise ValueError('订单不存在')

        if order.payment_status != PaymentStatusType.SUCCESS.value:
            raise ValueError('当前订单状态不允许退款')

        balance = db.query(BalanceModel).filter_by(
            user_id=order.user_id).order_by(desc('id')).value(text('balance'))
        if balance is None or balance < order.amount:
            raise ValueError('余额不足')

        balance = db.query(BalanceGiftModel).filter_by(
            user_id=order.user_id).order_by(desc('id')).value(text('balance'))
        if balance is not None and balance < order.gift_amount:
            raise ValueError('赠送余额不足')

        refund_status = False
        if order.payment_channel == PaymentChannelType.ALIPAY.value:
            alipay = payment_manager.get_instance(
                'alipay', appid=order.payment_appid)
            result = alipay.server_api(
                "alipay.trade.refund",
                biz_content={
                    'out_trade_no': order.trade_no,
                    'refund_amount': str(order.price)
                }
            )
            if result['code'] == '10000':
                refund_status = True
        else:
            raise ValueError(f'当前支付渠道 {order.payment_channel} 暂不支持自助退款')

        order.refund_response = json.dumps(result)
        if refund_status:
            order.payment_status = PaymentStatusType.REFUND_SUCCESS.value
        db.commit()

        if not refund_status:
            return

        task_data = {
            'type': BalanceType.REFUND.value,
            'user_id': order.user_id,
            'related_id': order.id,
            'amount': -1 * abs(order.amount),
            'balance': 0,
            'auto_memo': None,
            'back_memo': None,
            'ip': None
        }
        task_result = handle_balance.delay(task_data)
        logger.info(f'发送余额动账任务: {task_result.id}', extra=task_data)

        if order.gift_amount > 0:
            task_gift_data = {
                'type': BalanceType.REFUND.value,
                'user_id': order.user_id,
                'related_id': order.id,
                'amount': -1 * abs(order.gift_amount),
                'balance': 0,
                'auto_memo': None,
                'back_memo': None,
                'ip': None,
            }
            task_gift_result = handle_balance_gift.delay(task_gift_data)
            logger.info(
                f'发送赠送余额动账任务: {task_gift_result.id}', extra=task_gift_data)
