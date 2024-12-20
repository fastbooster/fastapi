#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/13 22:08


import traceback

import xmltodict
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse

from app.constants.constants import RESPONSE_WECHAT_SUCCESS, RESPONSE_WECHAT_FAIL, RESPONSE_ALIPAY_SUCCESS, \
    RESPONSE_ALIPAY_FAIL
from app.core.log import logger
from app.core.security import get_current_user_from_cache
from app.schemas.balance_recharge import BalanceRechargePublicItem
from app.schemas.finance import PaymentChannelType, RechargeForm, PayForm, ScanpayForm, \
    BalanceRechargeSettingListResponse
from app.services import balance_recharge

router = APIRouter()


@router.get('/balance_recharges', summary='余额充值订单列表')
def lists(user_data: dict = Depends(get_current_user_from_cache)):
    pass


@router.get('/balance_recharges/{trade_no}', summary='余额充值订单详情')
def detail(user_data: dict = Depends(get_current_user_from_cache)):
    pass


@router.get('/balance_recharges/settings', response_model=BalanceRechargeSettingListResponse,
            summary='余额充值套餐列表')
def settings():
    # TODO: BUG检测，接口本身不要求登录，但是 get 会要求登录，如果改成 post 则不需要
    items = balance_recharge.get_recharge_settings()
    # 给items每个元素添加一个id字段,其值为元素的索引值
    items = [{'id': i, **item} for i, item in enumerate(items)]
    return {"items": items}


@router.post('/balance_recharges/unifiedorder', summary='余额充值统一下单接口')
def unifiedorder(params: RechargeForm, request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        user_ip = request.client.host if request.client else None
        return balance_recharge.unifiedorder(params, user_data['id'], user_ip)
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值下单失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='余额充值下单失败')


@router.get('/balance_recharges/{trade_no}/check', response_model=BalanceRechargePublicItem,
            summary='余额充值检查订单支付结果')
def check(trade_no: str, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return balance_recharge.check_order(trade_no, user_data['id'])
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'检查余额充值结果失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='检查余额充值结果失败')


@router.post('/balance_recharges/pay', summary='支付触达 - 选择支付方式')
def pay(params: PayForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return balance_recharge.pay(params, user_data)
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值支付失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='余额充值支付失败：')


@router.post('/balance_recharges/scanpay',
             summary='支付触达 - 扫码支付（根据客户端类型(微信/支付宝/移动端浏览器)自动选择支付方式）')
def scanpay(params: ScanpayForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return balance_recharge.scanpay(params, user_data)
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值扫码支付失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='余额充值扫码支付失败')


@router.post("/balance_recharges/{payment_channel}/notify", summary="余额充值结果异步通知")
async def notify(payment_channel: str, request: Request):
    try:
        content = None
        match payment_channel:
            case (PaymentChannelType.WECHATPAY.value):
                body = await request.body()
                content = body.decode("utf-8")
                params = xmltodict.parse(content)['xml']
            case (PaymentChannelType.ALIPAY.value):
                formdata = await request.form()
                params = dict(formdata)
            case (_):
                raise HTTPException(status_code=400, detail=f'未知的支付渠道: {payment_channel}')
        result = balance_recharge.notify(payment_channel, params, content)
        response = RESPONSE_WECHAT_SUCCESS if payment_channel == 'wechatpay' else RESPONSE_ALIPAY_SUCCESS
        if not result:
            response = RESPONSE_WECHAT_FAIL if payment_channel == 'wechatpay' else RESPONSE_ALIPAY_FAIL
        return PlainTextResponse(response, status_code=200)
    except Exception as e:
        PlainTextResponse(RESPONSE_WECHAT_FAIL if payment_channel == 'wechatpay' else RESPONSE_ALIPAY_FAIL,
                          status_code=200)
        logger.error(f'余额充值结果异步通知处理失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
