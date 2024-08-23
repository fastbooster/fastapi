#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: FastBooster Generator
# Time: 2024-08-23 13:30

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.payment_config import PaymentConfigForm, PaymentConfigStatusForm, PaymentConfigItem, SearchQuery, \
    PaymentConfigListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import payment_config

router = APIRouter()


@router.get("/payment_configs", response_model=PaymentConfigListResponse,
            dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付配置列表")
def lists(params: SearchQuery = Depends()):
    return payment_config.lists(params)


@router.get("/payment_configs/{id}", response_model=PaymentConfigItem,
            dependencies=[Depends(check_permission('PaymentSettings'))],
            summary="支付配置详情", )
def detail(id: int):
    current_model = payment_config.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="支付配置不存在")
    return current_model


@router.post("/payment_configs", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PaymentSettings'))], summary="添加支付配置")
def add(params: PaymentConfigForm):
    try:
        payment_config.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加支付配置失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加支付配置失败')


@router.put("/payment_configs/{id}", response_model=ResponseSuccess,
            dependencies=[Depends(check_permission('PaymentSettings'))], summary="编辑支付配置")
def update(id: int, params: PaymentConfigForm):
    try:
        payment_config.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付配置失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑支付配置失败')


@router.patch("/payment_configs/{id}/status", response_model=ResponseSuccess,
              dependencies=[Depends(check_permission('PaymentSettings'))], summary="更新支付配置状态")
def update_status(id: int, params: PaymentConfigStatusForm):
    try:
        payment_config.update_status(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付配置失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑支付配置失败')


@router.delete("/payment_configs/{id}", response_model=ResponseSuccess,
               dependencies=[Depends(check_permission('PaymentSettings'))], summary="删除支付配置")
def delete(id: int):
    try:
        payment_config.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除支付配置失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除支付配置失败')


@router.post("/payment_configs/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PaymentSettings'))], summary="重建支付配置缓存")
def rebuild_cache():
    try:
        payment_config.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建支付配置缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建支付配置缓存失败')
