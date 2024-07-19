#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/19 00:58


import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.schemas.schemas import ResponseSuccess
from app.schemas.balance_recharge import BalanceRechargeSearchQuery, BalanceRechargeItem, BalanceRechargeListResponse

from app.core.security import check_permission
from app.services import balance_recharge as BalanceRechargeService


router = APIRouter()


@router.get('/balance_recharges', response_model=BalanceRechargeListResponse, dependencies=[Depends(check_permission('BalanceRecharges'))], summary='余额充值订单列表')
def lists(params: BalanceRechargeSearchQuery = Depends()):
    return BalanceRechargeService.get_balance_recharge_list(params)


@router.get('/balance_recharges/{trade_no}', response_model=BalanceRechargeItem, dependencies=[Depends(check_permission('BalanceRecharges'))], summary='余额充值订单详情')
def detail(trade_no: str):
    model = BalanceRechargeService.get_balance_recharge(trade_no=trade_no)
    if model is None:
        raise HTTPException(status_code=404, detail='余额充值订单不存在')
    return model


@router.post('/balance_recharges/{trade_no}/refund', response_model=ResponseSuccess, dependencies=[Depends(check_permission('BalanceRecharges'))], summary='余额充值订单退款')
def refund(trade_no: str):
    try:
        BalanceRechargeService.refund(trade_no)
        return ResponseSuccess()
    except ValueError as e:
        logger.error(f'退款失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'退款失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='退款失败')
