#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: adspace.py
# Author: FastBooster Generator
# Time: 2024-08-23 18:45

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.adspace import AdspaceForm, AdspaceItem, SearchQuery, AdspaceListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import adspace

router = APIRouter()


@router.get("/adspaces", response_model=AdspaceListResponse, dependencies=[Depends(check_permission('AdspaceList'))],
            summary="广告位列表")
def lists(params: SearchQuery = Depends()):
    return adspace.lists(params)


@router.get("/adspaces/{id}", response_model=AdspaceItem, dependencies=[Depends(check_permission('AdspaceList'))],
            summary="广告位详情", )
def detail(id: int):
    current_model = adspace.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="广告位不存在")
    return current_model


@router.post("/adspaces", response_model=ResponseSuccess, dependencies=[Depends(check_permission('AdspaceList'))],
             summary="添加广告位")
def add(params: AdspaceForm):
    try:
        adspace.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加广告位失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加广告位失败')


@router.put("/adspaces/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('AdspaceList'))],
            summary="编辑广告位")
def update(id: int, params: AdspaceForm):
    try:
        adspace.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑广告位失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑广告位失败')


@router.delete("/adspaces/{id}", response_model=ResponseSuccess,
               dependencies=[Depends(check_permission('AdspaceList'))], summary="删除广告位")
def delete(id: int):
    try:
        adspace.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除广告位失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除广告位失败')
