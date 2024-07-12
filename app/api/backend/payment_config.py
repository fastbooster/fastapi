#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_config.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/10 00:57

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import payment_config as PaymentConfigService

from app.schemas.schemas import ResponseSuccess
from app.schemas.payment_config import PaymentConfigItem, PaymentConfigSearchQuery, PaymentConfigListResponse

router = APIRouter()


@router.get("/payment_configs", response_model=PaymentConfigListResponse, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付配置列表")
def lists(params: PaymentConfigSearchQuery = Depends()):
    return PaymentConfigService.get_payment_config_list(params)


@router.get("/payment_configs/{id}", response_model=PaymentConfigItem, dependencies=[Depends(check_permission('PaymentSettings'))], summary="支付配置详情",)
def detail(id: int):
    item = PaymentConfigService.get_payment_config(id)
    if not item:
        raise HTTPException(status_code=404, detail="支付配置不存在")
    return item


@router.post("/payment_configs", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="添加支付配置")
def add(params: PaymentConfigItem):
    try:
        PaymentConfigService.add_payment_config(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加支付配置失败：{e}')
        raise HTTPException(status_code=500, detail='添加支付配置失败')
    return ResponseSuccess


@router.put("/payment_configs/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="编辑支付配置")
def edit(id: int, params: PaymentConfigItem):
    try:
        params.id = id
        PaymentConfigService.edit_payment_config(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付配置失败：{e}')
        raise HTTPException(status_code=500, detail='编辑支付配置失败')
    return ResponseSuccess


@router.patch("/payment_configs/{id}/status", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="更新支付配置状态")
def update_status(id: int, params: PaymentConfigItem):
    try:
        params.id = id
        PaymentConfigService.update_status(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑支付配置失败：{e}')
        raise HTTPException(status_code=500, detail='编辑支付配置失败')
    return ResponseSuccess


@router.delete("/payment_configs/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="删除支付配置",)
def delete(id: int):
    try:
        PaymentConfigService.delete_payment_config(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除支付配置失败：{e}')
        raise HTTPException(status_code=500, detail='删除支付配置失败')
    return ResponseSuccess


@router.post("/payment_configs/rebuild_cache", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PaymentSettings'))], summary="重建缓存",)
def rebuild_cache():
    try:
        PaymentConfigService.rebuild_cache()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建缓存失败：{e}')
        raise HTTPException(status_code=500, detail='重建缓存失败')
    return ResponseSuccess
