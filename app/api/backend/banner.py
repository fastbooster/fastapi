#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: banner.py
# Author: FastBooster Generator
# Time: 2024-08-23 19:52

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.banner import BannerForm, BannerItem, SearchQuery, BannerListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import banner

router = APIRouter()


@router.get("/banners", response_model=BannerListResponse, dependencies=[Depends(check_permission('BannerList'))],
            summary="广告资源列表")
def lists(params: SearchQuery = Depends()):
    return banner.lists(params)


@router.get("/banners/{id}", response_model=BannerItem, dependencies=[Depends(check_permission('BannerList'))],
            summary="广告资源详情", )
def detail(id: int):
    current_model = banner.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="广告资源不存在")
    return current_model


@router.post("/banners", response_model=ResponseSuccess, dependencies=[Depends(check_permission('BannerList'))],
             summary="添加广告资源")
def add(params: BannerForm):
    try:
        banner.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加广告资源失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加广告资源失败')


@router.put("/banners/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('BannerList'))],
            summary="编辑广告资源")
def update(id: int, params: BannerForm):
    try:
        banner.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑广告资源失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑广告资源失败')


@router.delete("/banners/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('BannerList'))],
               summary="删除广告资源")
def delete(id: int):
    try:
        banner.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除广告资源失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除广告资源失败')


@router.post("/banners/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('BannerList'))], summary="重建广告资源缓存")
def rebuild_cache():
    try:
        banner.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建广告资源缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建广告资源缓存失败')
