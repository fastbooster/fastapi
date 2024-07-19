#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ad.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/29 20:56

from fastapi import APIRouter, HTTPException, Depends
from app.core.log import logger

from app.constants.constants import RESPONSE_OK
from app.core.security import check_permission
from app.schemas.ad import SpaceSearchQuery, SpaceAddForm, SpaceEditForm, AdSearchQuery, AdAddForm, AdEditForm
from app.services import ad as AdService

router = APIRouter()


@router.get("/ad_space", dependencies=[Depends(check_permission('AdSpaceList'))], summary="广告位列表")
def space_list(params: SpaceSearchQuery = Depends()):
    return AdService.get_space_list(params)


@router.get("/ad_space/{id}", dependencies=[Depends(check_permission('AdSpaceList'))], summary="广告位详情", )
def space_detail(id: int):
    ad_space = AdService.get_space(id)
    if not ad_space:
        raise HTTPException(status_code=404, detail="广告位不存在")
    return ad_space


@router.post("/ad_space", dependencies=[Depends(check_permission('AdSpaceList'))], summary="添加广告位")
def add_space(params: SpaceAddForm):
    try:
        AdService.add_space(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加广告位失败：{e}')
        raise HTTPException(status_code=500, detail='添加广告位失败')
    return RESPONSE_OK


@router.patch("/ad_space", dependencies=[Depends(check_permission('AdSpaceList'))], summary="编辑广告位")
def edit_space(params: SpaceEditForm):
    try:
        AdService.edit_space(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑广告位失败：{e}')
        raise HTTPException(status_code=500, detail='编辑广告位失败')
    return RESPONSE_OK


@router.delete("/ad_space/{id}", dependencies=[Depends(check_permission('AdSpaceList'))], summary="删除广告位", )
def delete_space(id: int):
    try:
        AdService.delete_space(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除广告位失败：{e}')
        raise HTTPException(status_code=500, detail='删除广告位失败')
    return RESPONSE_OK


@router.post("/ad_space/rebuild_cache", dependencies=[Depends(check_permission('AdSpaceList'))],
           summary="重建广告位缓存", )
def rebuild_cache():
    try:
        AdService.rebuild_cache()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建广告位缓存失败：{e}')
        raise HTTPException(status_code=500, detail='重建广告位缓存失败')
    return RESPONSE_OK


@router.get("/ad", dependencies=[Depends(check_permission('AdSpaceList'))], summary="广告列表")
def ad_list(params: AdSearchQuery = Depends()):
    return AdService.get_ad_list(params)


@router.get("/ad/{id}", dependencies=[Depends(check_permission('AdSpaceList'))], summary="广告详情", )
def ad_detail(id: int):
    ad = AdService.get_ad(id)
    if not ad:
        raise HTTPException(status_code=404, detail="广告不存在")
    return ad


@router.post("/ad", dependencies=[Depends(check_permission('AdSpaceList'))], summary="添加广告")
def add_ad(params: AdAddForm):
    try:
        AdService.add_ad(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加广告失败：{e}')
        raise HTTPException(status_code=500, detail='添加广告失败')
    return RESPONSE_OK


@router.patch("/ad", dependencies=[Depends(check_permission('AdSpaceList'))], summary="编辑广告")
def edit_ad(params: AdEditForm):
    try:
        AdService.edit_ad(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑广告失败：{e}')
        raise HTTPException(status_code=500, detail='编辑广告失败')
    return RESPONSE_OK


@router.delete("/ad/{id}", dependencies=[Depends(check_permission('AdSpaceList'))], summary="删除广告", )
def delete_ad(id: int):
    try:
        AdService.delete_ad(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除广告失败：{e}')
        raise HTTPException(status_code=500, detail='删除广告失败')
    return RESPONSE_OK
