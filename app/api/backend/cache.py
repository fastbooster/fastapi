#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File: cache.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/8/30 16:45

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.cache import CacheListResponse, CacheDetailResponse
from app.schemas.schemas import ResponseSuccess
from app.services import cache

router = APIRouter()


@router.get("/caches", response_model=CacheListResponse, dependencies=[Depends(check_permission('CacheList'))],
            summary="缓存列表")
def lists():
    return cache.lists()


@router.get("/caches/{key}", response_model=CacheDetailResponse, dependencies=[Depends(check_permission('CacheList'))],
            summary="缓存详情")
def detail(key: str):
    try:
        return cache.detail(key)
    except Exception as e:
        logger.error(f'获取缓存详情失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail=f'获取缓存详情失败（{e}）')


@router.post("/caches/{key}/rebuild", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('CacheList'))], summary="重建缓存")
def rebuild_cache(key: str):
    try:
        cache.rebuild_cache(key)
        return ResponseSuccess()
    except Exception as e:
        logger.error(f'重建微信媒体平台缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail=f'重建缓存失败: {e}')
