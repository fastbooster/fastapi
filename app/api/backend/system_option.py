#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 15:13

from loguru import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import system_option as OptionService

from app.schemas.system_option import OptionSearchQuery, OptionAddForm, OptionEditForm
from app.constants.constants import RESPONSE_OK

router = APIRouter()


@router.get("/options", dependencies=[Depends(check_permission('SystemOption'))], summary="系统选项列表")
def option_list(params: OptionSearchQuery = Depends()):
    return OptionService.get_user_list(params)


@router.get("/options/{id}", dependencies=[Depends(check_permission('SystemOption'))], summary="系统选项详情",)
def option_detail(id: int):
    option = OptionService.get_user(id)
    if not option:
        raise HTTPException(status_code=404, detail="系统选项不存在")
    return option


@router.post("/options", dependencies=[Depends(check_permission('SystemOption'))], summary="添加系统选项")
def add_option(params: OptionAddForm):
    try:
        OptionService.add_option(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='添加系统选项失败')
    return RESPONSE_OK


@router.put("/options", dependencies=[Depends(check_permission('SystemOption'))], summary="编辑系统选项")
def edit_option(params: OptionEditForm):
    try:
        OptionService.edit_option(params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='编辑系统选项失败')
    return RESPONSE_OK


@router.delete("/options/{id}", dependencies=[Depends(check_permission('SystemOption'))], summary="删除系统选项",)
def delete_option(id: int):
    try:
        OptionService.delete_option(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除系统选项失败：{e}')
        raise HTTPException(status_code=500, detail='删除系统选项失败')
    return RESPONSE_OK


@router.put("/options/rebuild_cache", dependencies=[Depends(check_permission('SystemOption'))], summary="重建系统选项缓存",)
def rebuild_cache():
    try:
        OptionService.rebuild_cache()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建系统选项缓存失败：{e}')
        raise HTTPException(status_code=500, detail='重建系统选项缓存失败')
    return RESPONSE_OK
