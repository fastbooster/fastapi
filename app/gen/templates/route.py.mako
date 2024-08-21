#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ${file_name}
# Author: FastBooster Generator
# Time: ${create_time}

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.schemas import ResponseSuccess
from app.schemas.${snake_name} import ${model}Form, ${model}Item, SearchQuery, ${model}ListResponse
from app.services import ${snake_name}

router = APIRouter()


@router.get("/${route}", response_model=${model}ListResponse, dependencies=[Depends(check_permission('${model}List'))], summary="${name}列表")
def lists(params: SearchQuery = Depends()):
    return ${snake_name}.lists(params)


@router.get("/${route}/{id}", response_model=${model}Item, dependencies=[Depends(check_permission('${model}List'))],
            summary="${name}详情", )
def detail(id: int):
    item = ${snake_name}.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="${name}不存在")
    return item


@router.post("/${route}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('${model}List'))],
             summary="添加${name}")
def add(params: ${model}Form):
    try:
        ${snake_name}.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加${name}失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加${name}失败')


@router.put("/${route}/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('${model}List'))],
            summary="编辑${name}")
def update(id: int, params: ${model}Form):
    try:
        ${snake_name}.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑${name}失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑${name}失败')


@router.delete("/${route}/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('${model}List'))], summary="删除${name}")
def delete(id: int):
    try:
        ${snake_name}.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除${name}失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除${name}失败')


@router.post("/${route}/rebuild_cache", response_model=ResponseSuccess, dependencies=[Depends(check_permission('${model}List'))], summary="重建${name}缓存")
def rebuild_cache():
    try:
        ${snake_name}.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建${name}缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建${name}缓存失败')
