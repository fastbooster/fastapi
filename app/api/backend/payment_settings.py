#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/10 00:57

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import payment_settings as PaymentSettingService
from app.services import system_option as SystemOptionService

from app.schemas.schemas import ResponseSuccess
from app.schemas.system_option import OptionItem
from app.schemas.payment_settings import PaymentSettingsSortForm, PaymentSettingListResponse

router = APIRouter()


@router.get("/payment_settings", response_model=PaymentSettingListResponse, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付设置列表")
def lists():
    return PaymentSettingService.get_payment_settings()


@router.patch("/payment_settings/sort", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付设置排序")
def lists(params: PaymentSettingsSortForm):
    try:
        PaymentSettingService.update_sort(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'更新排序失败：{e}')
        raise HTTPException(status_code=500, detail='更新排序失败')

    return ResponseSuccess


@router.get("/payment_settings/alipay_root_cert", response_model=OptionItem, dependencies=[Depends(check_permission('PaymentSettings'))], summary="获取支付宝根证书")
def get_point_recharge_settings():
    return SystemOptionService.get_option_by_name('alipay_root_cert')


@router.put("/payment_settings/alipay_root_cert", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="设置支付宝根证书")
def alipay_root_cert(params: OptionItem):
    try:
        SystemOptionService.autoupdate(OptionItem(
            option_name='alipay_root_cert',
            option_value=params.option_value,
            autoload=1,
            lock=1,
            memo="支付宝根证书"
        ))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'设置支付宝根证书失败：{e}')
        raise HTTPException(status_code=500, detail='设置支付宝根证书失败')

    return ResponseSuccess
