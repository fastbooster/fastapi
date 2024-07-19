#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:13

from app.core.log import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import system_option as OptionService

from app.schemas.schemas import ResponseSuccess
from app.schemas.system_option import OptionItem, OptionSearchQuery, OptionListResponse

router = APIRouter()


@router.get("/options", response_model=OptionListResponse, dependencies=[Depends(check_permission('SystemOption'))], summary="系统选项列表")
def lists(params: OptionSearchQuery = Depends()):
    return OptionService.get_option_list(params)


@router.get("/options/{id}", response_model=OptionItem, dependencies=[Depends(check_permission('SystemOption'))], summary="系统选项详情",)
def detail(id: int):
    option = OptionService.get_option(id)
    if not option:
        raise HTTPException(status_code=404, detail="系统选项不存在")
    return option


@router.post("/options", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))], summary="添加系统选项")
def add(params: OptionItem):
    try:
        OptionService.add_option(params)
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='添加系统选项失败')


@router.put("/options/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))], summary="编辑系统选项")
def edit(id: int, params: OptionItem):
    try:
        params.id = id
        OptionService.edit_option(params)
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='编辑系统选项失败')


@router.delete("/options/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))], summary="删除系统选项",)
def delete(id: int):
    try:
        OptionService.delete_option(id)
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='删除系统选项失败')


@router.post("/options/rebuild_cache", response_model=ResponseSuccess, dependencies=[Depends(check_permission('SystemOption'))], summary="重建系统选项缓存",)
def rebuild_cache():
    try:
        OptionService.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建系统选项缓存失败：{e}')
        raise HTTPException(status_code=500, detail='重建系统选项缓存失败')
