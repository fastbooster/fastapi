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

from app.schemas.schemas import ResponseSuccess, StatusType
from app.schemas.payment_config import PaymentConfigItem, PaymentConfigSearchQuery, PaymentConfigListResponse
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
