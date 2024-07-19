#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 12:07

from app.core.log import logger

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List

from app.core.security import check_permission, get_current_user_from_cache
from app.services import finance as FinanceService

from app.schemas.schemas import ResponseSuccess
from app.schemas.finance import SearchQuery, AdjustForm, PaymentAccountSearchQuery, \
    PointRechargeSettingItem, BalanceRechargeSettingItem, \
    PointRechargeSettingListResponse, BalanceRechargeSettingListResponse


router = APIRouter()


@router.get("/finance/balance", dependencies=[Depends(check_permission('UserList'))], summary="获取余额列表")
def balance_list(params: SearchQuery = Depends()):
    return FinanceService.get_balance_list(params)


@router.get("/finance/balance_gift", dependencies=[Depends(check_permission('UserList'))], summary="获取赠送余额列表")
def balance_gift_list(params: SearchQuery = Depends()):
    return FinanceService.get_balance_gift_list(params)


@router.get("/finance/point", dependencies=[Depends(check_permission('UserList'))], summary="获取积分列表")
def point_list(params: SearchQuery = Depends()):
    return FinanceService.get_point_list(params)


@router.post("/finance/adjust_balance", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
             summary="调整指定用户余额余额")
def adjust_balance(params: AdjustForm, request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        params.ip = request.client.host if request.client else None,
        FinanceService.adjust_balance(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'调整余额余额失败：{e}')
        raise HTTPException(status_code=500, detail='调整余额余额失败')
    return ResponseSuccess


@router.post("/finance/adjust_balance_gift", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
             summary="调整指定用户赠送余额余额")
def adjust_balance(params: AdjustForm, request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        params.ip = request.client.host if request.client else None,
        FinanceService.adjust_balance_gift(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'调整赠送余额余额失败：{e}')
        raise HTTPException(status_code=500, detail='调整赠送余额余额失败')
    return ResponseSuccess


@router.post("/finance/adjust_point", response_model=ResponseSuccess, dependencies=[Depends(check_permission('UserList'))],
             summary="调整指定用户积分余额")
def adjust_point(params: AdjustForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        FinanceService.adjust_point(params, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'调整积分余额失败：{e}')
        raise HTTPException(status_code=500, detail='调整积分余额失败')
    return ResponseSuccess


@router.get("/finance/payment_account", dependencies=[Depends(check_permission('UserList'))], summary="支付账号列表")
def get_payment_account_list(params: PaymentAccountSearchQuery = Depends()):
    return FinanceService.get_payment_account_list(params)


@router.get("/finance/point_recharge_settings", response_model=PointRechargeSettingListResponse, dependencies=[Depends(check_permission('RechargeSettings'))], summary="获取积分充值设置")
def get_point_recharge_settings():
    return {"items": FinanceService.get_point_recharge_settings()}


@router.put("/finance/point_recharge_settings", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RechargeSettings'))],
            summary="更新积分充值设置")
def update_point_recharge_settings(settings: List[PointRechargeSettingItem]):
    try:
        FinanceService.update_point_recharge_settings(settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'更新积分充值设置失败：{e}')
        raise HTTPException(status_code=500, detail='更新积分充值设置失败')
    return ResponseSuccess


@router.get("/finance/balance_recharge_settings", response_model=BalanceRechargeSettingListResponse, dependencies=[Depends(check_permission('RechargeSettings'))], summary="获取余额充值设置")
def get_balance_recharge_settings():
    return {"items": FinanceService.get_balance_recharge_settings()}


@router.put("/finance/balance_recharge_settings", response_model=ResponseSuccess, dependencies=[Depends(check_permission('RechargeSettings'))],
            summary="更新余额充值设置")
def update_balance_recharge_settings(settings: List[BalanceRechargeSettingItem]):
    try:
        FinanceService.update_balance_recharge_settings(settings)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'更新余额充值设置失败：{e}')
        raise HTTPException(status_code=500, detail='更新余额充值设置失败')
    return ResponseSuccess
