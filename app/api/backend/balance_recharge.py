#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: balance_recharge.py
# Author: FastBooster Generator
# Time: 2024-08-23 22:09

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.balance_recharge import BalanceRechargeItem, SearchQuery, BalanceRechargeListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import balance_recharge

router = APIRouter()


@router.get("/balance_recharges", response_model=BalanceRechargeListResponse,
            dependencies=[Depends(check_permission('BalanceRechargeList'))], summary="余额充值日志列表")
def lists(params: SearchQuery = Depends()):
    return balance_recharge.lists(params)


@router.get("/balance_recharges/{trade_no}", response_model=BalanceRechargeItem,
            dependencies=[Depends(check_permission('BalanceRechargeList'))],
            summary="余额充值日志详情")
def detail(trade_no: str):
    current_model = balance_recharge.get(trade_no=trade_no)
    if not current_model:
        raise HTTPException(status_code=404, detail="余额充值日志不存在")
    return current_model


@router.post('/balance_recharges/{trade_no}/refund', response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('BalanceRechargeList'))], summary='余额充值订单退款')
def refund(trade_no: str):
    try:
        balance_recharge.refund(trade_no)
        return ResponseSuccess()
    except ValueError as e:
        logger.error(f'退款失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'退款失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='退款失败')
