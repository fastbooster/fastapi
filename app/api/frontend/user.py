#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 20:13

import traceback

from fastapi import APIRouter, HTTPException, Depends, Request

from app.core.security import get_current_user_from_cache
from app.services import user as UserService
from app.services import finance as FinanceService
from app.core.log import logger
from app.schemas.schemas import ResponseSuccess
from app.schemas.finance import PaymentAccountFrontendSearchQuery, PaymentAccountAddForm, PaymentAccountEditForm

router = APIRouter()


@router.get("/user/me", summary="我的详情")
def my_detail(user_data: dict = Depends(get_current_user_from_cache)):
    return UserService.safe_whitelist_fields(user_data)


@router.post("/user/checkin", response_model=ResponseSuccess, summary="用户签到")
def checkin(request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        ip = request.client.host if request.client else None
        user_agent = str(request.headers.get('User-Agent'))
        FinanceService.checkin(user_data['id'], ip, user_agent)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'签到失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='签到失败')


@router.get("/user/payment_account", summary="支付账号列表")
def get_payment_account_list(params: PaymentAccountFrontendSearchQuery = Depends(),
                             user_data: dict = Depends(get_current_user_from_cache)):
    return FinanceService.get_payment_account_list_frontend(params, user_data['id'])


@router.post("/user/payment_account", response_model=ResponseSuccess, summary="绑定支付账号")
def add_payment_account(params: PaymentAccountAddForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        FinanceService.add_payment_account(params, user_data['id'])
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'绑定支付账号失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='绑定支付账号失败')


@router.patch("/user/payment_account", response_model=ResponseSuccess, summary="编辑支付账号")
def add_payment_account(params: PaymentAccountEditForm, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        FinanceService.edit_payment_account(params, user_data['id'])
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付账号失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑支付账号失败')


@router.delete("/user/payment_account/{id}", response_model=ResponseSuccess, summary="删除支付账号")
def add_payment_account(id: int, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        FinanceService.delete_payment_account(id, user_data['id'])
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除支付账号失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除支付账号失败')
