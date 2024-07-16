#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/16 15:51


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
from app.schemas.finance import SearchQuery, AdjustForm, CheckinType, BalanceType, PointType, PaymentAccountSearchQuery, \
    PaymentAccountFrontendSearchQuery, PaymentAccountAddForm, PaymentAccountEditForm, PointRechargeSettingItem, \
    BalanceRechargeSettingItem, PaymentStatuType, RechargeForm, PayForm, ScanpayForm, PaymentChannelType
from app.schemas.config import Settings
from app.schemas.schemas import ClientType
from app.tasks.finance import handle_balance, handle_balance_gift, handle_point
from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD
from app.services import system_option as SystemOptionService
from app.core.payment import payment_manager


def pay(params: PayForm, user_data: dict) -> dict:
    '''TODO: 定义返回数据模型'''
    with get_session() as db:
        order_model = db.query(BalanceRechargeModel).filter_by(
            trade_no=params.trade_no).first()
        if order_model is None or order_model.user_id != user_data['id'] or order_model.payment_status != PaymentStatuType.PAYMENT_STATUS_CREATED.value:
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
            notify_url=f"{settings.ENDPOINT.pay.rstrip(
                '/')}/api/v1/frontend/balance_recharges/wechat/notify",
            openid=openid,
        )
        if 'return_code' not in result or result['return_code'] != 'SUCCESS' or result['result_code'] != 'SUCCESS':
            error_msg = result.get('return_msg', '')
            error_code_des = result.get('err_code_des', '')
            raise ValueError(f"Get Wechat API Error: {error_msg}{
                             error_code_des}", result, result.get('return_code'))

        if 'timestamp' not in result:
            result['timestamp'] = str(int(time.time()))
        return result

    if params.channel == 'alipay':
        alipay = payment_manager.get_instance('alipay', params.appid)
        api_name = 'alipay.trade.wap.pay'
        product_code = 'FAST_INSTANT_TRADE_PAY'
        return_url = params.return_url
        match (params.client):
            case ClientType.PC_BROWSER:
                api_name = 'alipay.trade.page.pay'
                return_url = settings.ENDPOINT.portal
            case ClientType.MOBILE_BROWSER | ClientType.ALIPAY_BROWSER | ClientType.WECHAT_BROWSER:
                api_name = 'alipay.trade.wap.pay'
                return_url = settings.ENDPOINT.mp
            case ClientType.ANDROID_APP | ClientType.IOS_APP:
                api_name = 'alipay.trade.app.pay'
                product_code = 'QUICK_MSECURITY_PAY'
                raise ValueError('尚未支持APP客户端支付')
            case (_):
                raise ValueError('不支持的客户端类型')

        order_string = alipay.client_api(
            api_name,
            biz_content={
                "out_trade_no": params.trade_no,
                "total_amount": float(price),
                "subject": "余额充值",
                "product_code": product_code,
            },
            return_url=return_url,
            notify_url=f"{settings.ENDPOINT.pay.rstrip(
                '/')}/api/v1/frontend/balance_recharges/alipay/notify"
        )
        return {'url': f"{alipay._gateway}?{order_string}"}


def notify(payment_channel: str, params: dict, content: str = None) -> bool:
    logger.info(f'收到异步通知: {payment_channel}', extra=params)
    if payment_channel == PaymentChannelType.ALIPAY.value:
        signature = params.pop('sign')
        alipay = payment_manager.get_instance('alipay', params.get('app_id', None))
        try:
            success = alipay.verify(params, signature)
        except:
            logger.error(f'签名验证失败: {payment_channel}', extra=params)
            return False
        if not success:
            logger.error(f'签名验证失败: {payment_channel}', extra=params)
            return False
        is_ok = True if params["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED") else False
    elif payment_channel == PaymentChannelType.WECHATPAY.value:
        # 如果是微信小程序支付, appid 返回的是小程序的 appid, 由于已经做了缓存适配，可以直接使用 appid 参数
        wechatpy = payment_manager.get_instance('wechat', params.get('appid', None))
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
        order_model = db.query(BalanceRechargeModel).filter_by(trade_no=params.get('out_trade_no')).first()
        if order_model is None:
            logger.info('订单不存在', extra=params)
            return False
        if order_model.payment_status not in (
        PaymentStatuType.PAYMENT_STATUS_CREATED.value, PaymentStatuType.PAYMENT_STATUS_CLOSE.value):
            logger.info(f'订单状态异常: payment_status={order_model.payment_status}, 不接受异步通知', extra=params)
            return True

        order_model.payment_status = PaymentStatuType.PAYMENT_STATUS_SUCCESS.value if is_ok else PaymentStatuType.PAYMENT_STATUS_FAIL.value
        order_model.payment_tool = payment_channel
        order_model.payment_time = datetime.now()
        order_model.payment_response = json.dumps(params)

        # 余额变动
        if is_ok:
            task_data = {
                'type': BalanceType.TYPE_RECHARGE.value,
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
                    'type': BalanceType.TYPE_RECHARGE_GIFT.value,
                    'user_id': order_model.user_id,
                    'related_id': order_model.id,
                    'amount': order_model.gift_amount,
                    'balance': 0,
                    'auto_memo': '用户充值赠送',
                    'back_memo': None,
                    'ip': order_model.user_ip,
                }
                task_gift_result = handle_balance.delay(task_gift_data)
                logger.info(f'发送余额动账任务: {task_gift_result.id}', extra=task_gift_data)

            logger.info('成功受理通知', extra=params)

        db.commit()

        return is_ok
