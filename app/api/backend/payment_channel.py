#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: FastBooster Generator
# Time: 2024-08-23 12:11

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.payment_channel import PaymentChannelForm, PaymentChannelItem, SearchQuery, PaymentChannelListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import payment_channel

router = APIRouter()


@router.get("/payment_channels", response_model=PaymentChannelListResponse,
            dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付渠道列表")
def lists(params: SearchQuery = Depends()):
    return payment_channel.lists(params)


@router.get("/payment_channels/{id}", response_model=PaymentChannelItem,
            dependencies=[Depends(check_permission('PaymentSettings'))],
            summary="支付渠道详情", )
def detail(id: int):
    current_model = payment_channel.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="支付渠道不存在")
    return current_model


@router.post("/payment_channels", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PaymentSettings'))], summary="添加支付渠道")
def add(params: PaymentChannelForm):
    try:
        payment_channel.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加支付渠道失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加支付渠道失败')


@router.put("/payment_channels/{id}", response_model=ResponseSuccess,
            dependencies=[Depends(check_permission('PaymentSettings'))], summary="编辑支付渠道")
def update(id: int, params: PaymentChannelForm):
    try:
        payment_channel.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付渠道失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑支付渠道失败')


@router.delete("/payment_channels/{id}", response_model=ResponseSuccess,
               dependencies=[Depends(check_permission('PaymentSettings'))], summary="删除支付渠道")
def delete(id: int):
    try:
        payment_channel.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除支付渠道失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除支付渠道失败')


@router.post("/payment_channels/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PaymentSettings'))], summary="重建支付渠道缓存")
def rebuild_cache():
    try:
        payment_channel.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建支付渠道缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建支付渠道缓存失败')
