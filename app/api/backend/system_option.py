#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:13

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.schemas import ResponseSuccess
from app.schemas.system_option import SearchQuery, SystemOptionForm, SystemOptionItem, SystemOptionResponse
from app.services import system_option

router = APIRouter()


@router.get("/options", response_model=SystemOptionResponse, dependencies=[Depends(check_permission('SystemOption'))],
            summary="系统选项列表")
def lists(params: SearchQuery = Depends()):
    return system_option.lists(params)


@router.get("/options/{id}", response_model=SystemOptionItem, dependencies=[Depends(check_permission('SystemOption'))],
            summary="系统选项详情", )
def detail(id: int):
    current_model = system_option.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="系统选项不存在")
    return current_model


@router.post("/options", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))],
             summary="添加系统选项")
def add(params: SystemOptionForm):
    try:
        system_option.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加系统选项失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加系统选项失败')


@router.put("/options/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))],
            summary="编辑系统选项")
def update(id: int, params: SystemOptionForm):
    try:
        system_option.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑系统选项失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑系统选项失败')


@router.delete("/options/{id}", response_model=ResponseSuccess,
               dependencies=[Depends(check_permission('SystemOption'))], summary="删除系统选项", )
def delete(id: int):
    try:
        system_option.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除系统选项失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除系统选项失败')


@router.post("/options/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('SystemOption'))], summary="重建系统选项缓存", )
def rebuild_cache():
    try:
        system_option.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建系统选项缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建系统选项缓存失败')
