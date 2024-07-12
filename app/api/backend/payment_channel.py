#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_channel.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 11:51

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import payment_channel as PaymentChannelService

from app.schemas.schemas import ResponseSuccess
from app.schemas.payment_channel import PaymentChannelItem, PaymentChannelSearchQuery, PaymentChannelListResponse

router = APIRouter()


@router.get("/payment_channels", response_model=PaymentChannelListResponse, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付渠道列表")
def lists(params: PaymentChannelSearchQuery = Depends()):
    return PaymentChannelService.get_payment_channel_list(params)


@router.get("/payment_channels/{id}", response_model=PaymentChannelItem, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付渠道详情",)
def detail(id: int):
    item = PaymentChannelService.get_payment_channel(id)
    if not item:
        raise HTTPException(status_code=404, detail="支付渠道不存在")
    return item


@router.post("/payment_channels", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="添加支付渠道")
def add(params: PaymentChannelItem):
    try:
        PaymentChannelService.add_payment_channel(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加支付渠道失败：{e}')
        raise HTTPException(status_code=500, detail='添加支付渠道失败')
    return ResponseSuccess


@router.put("/payment_channels/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="编辑支付渠道")
def edit(id: int, params: PaymentChannelItem):
    try:
        params.id = id
        PaymentChannelService.edit_payment_channel(params)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f'键异常: {e}')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付渠道失败：{e}')
        raise HTTPException(status_code=500, detail='编辑支付渠道失败')
    return ResponseSuccess


@router.delete("/payment_channels/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="删除支付渠道",)
def delete(id: int):
    try:
        PaymentChannelService.delete_payment_channel(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除支付渠道失败：{e}')
        raise HTTPException(status_code=500, detail='删除支付渠道失败')
    return ResponseSuccess


@router.post("/payment_channels/rebuild_cache", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="重建缓存",)
def rebuild_cache():
    try:
        PaymentChannelService.rebuild_cache()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建缓存失败：{e}')
        raise HTTPException(status_code=500, detail='重建缓存失败')
    return ResponseSuccess
