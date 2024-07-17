#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/6/3 17:43

import xmltodict
from app.core.log import logger

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import PlainTextResponse

from app.schemas.finance import RechargeForm, PayForm, ScanpayForm, PointRechargeSettingListResponse, BalanceRechargeSettingListResponse
from app.schemas.payment_settings import PaymentSettingOutListResponse

from app.core.security import get_current_user_from_cache
from app.services import finance as FinanceService
from app.services import payment_settings as PaymentSettingsService

from app.constants.constants import RESPONSE_WECHAT_SUCCESS, RESPONSE_WECHAT_FAIL, RESPONSE_ALIPAY_SUCCESS, \
    RESPONSE_ALIPAY_FAIL

router = APIRouter()


@router.get('/finance/payment_settings', response_model=PaymentSettingOutListResponse, summary='获取支付设置 (from cache)')
def payment_settings():
    return PaymentSettingsService.get_payment_settings_from_cache()


@router.get('/finance/point/recharge_settings', response_model=PointRechargeSettingListResponse, summary='积分充值套餐列表')
def point_setting():
    items = FinanceService.get_point_recharge_settings()
    # 给items每个元素添加一个id字段,其值为元素的索引值
    items = [{'id': i, **item} for i, item in enumerate(items)]
    return {"items": items}


@router.get('/finance/balance/recharge_settings', response_model=BalanceRechargeSettingListResponse, summary='余额充值套餐列表')
def balance_setting():
    items = FinanceService.get_balance_recharge_settings()
    # 给items每个元素添加一个id字段,其值为元素的索引值
    items = [{'id': i, **item} for i, item in enumerate(items)]
    return {"items": items}


@router.post('/finance/point/unifiedorder', summary='积分充值统一下单接口')
def point_unifiedorder(params: RechargeForm, request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        user_ip = request.client.host if request.client else None
        return FinanceService.point_unifiedorder(params, user_data['id'], user_ip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'积分充值下单失败：{e}')
        raise HTTPException(status_code=500, detail='积分充值下单失败')


@router.post('/finance/balance/unifiedorder', summary='余额充值统一下单接口')
def balance_unifiedorder(params: RechargeForm, request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        user_ip = request.client.host if request.client else None
        return FinanceService.balance_unifiedorder(params, user_data['id'], user_ip)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值下单失败：{e}')
        raise HTTPException(status_code=500, detail='余额充值下单失败')


@router.get('/finance/point/check{trade_no}', summary='积分充值检查支付结果')
def point_check(trade_no: str, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return FinanceService.point_check(trade_no, user_data['id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'检查积分充值结果失败：{e}')
        raise HTTPException(status_code=500, detail='检查积分充值结果失败')


@router.get('/finance/balance/check{trade_no}', summary='余额充值检查支付结果')
def balance_check(trade_no: str, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return FinanceService.balance_check(trade_no, user_data['id'])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'检查余额充值结果失败：{e}')
        raise HTTPException(status_code=500, detail='检查余额充值结果失败')


@router.post('/finance/point/scanpay', summary='积分充值扫码支付触达')
def point_scanpay(params: ScanpayForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return FinanceService.point_scanpay(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'积分充值扫码支付失败：{e}')
        raise HTTPException(status_code=500, detail='积分充值扫码支付失败')


@router.post('/finance/balance/scanpay', summary='余额充值扫码支付触达')
def balance_scanpay(params: ScanpayForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return FinanceService.balance_scanpay(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值扫码支付失败：{e}')
        raise HTTPException(status_code=500, detail='余额充值扫码支付失败')


@router.post('/finance/balance/pay', summary='余额充值选择支付方式直接触达')
def balance_scanpay(params: PayForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        return FinanceService.balance_recharge_pay(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'余额充值扫码支付失败：{e}')
        raise HTTPException(status_code=500, detail='余额充值扫码支付失败')


@router.post("/finance/{payment_channel}/point/notify", summary="积分充值结果通知")
async def point_notify(payment_channel: str, request: Request):
    try:
        content = None
        params = dict(request.query_params)
        if payment_channel == 'wechat':
            body = await request.body()
            content = body.decode("utf-8")
            params = xmltodict.parse(content)['xml']

        result = FinanceService.point_notify(payment_channel, params, content)

        response = RESPONSE_WECHAT_SUCCESS if payment_channel == 'wechat' else RESPONSE_ALIPAY_SUCCESS
        if not result:
            response = RESPONSE_WECHAT_FAIL if payment_channel == 'wechat' else RESPONSE_ALIPAY_FAIL

        return PlainTextResponse(response, status_code=200)
    except Exception as e:
        logger.error(f'积分充值结果通知处理失败：{e}')
        PlainTextResponse(RESPONSE_WECHAT_FAIL if payment_channel == 'wechat' else RESPONSE_ALIPAY_FAIL, status_code=200)
