#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/06 01:57

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.schemas import ResponseSuccess
from app.schemas.wechat import WechatForm, WechatItem, SearchQuery, WechatListResponse
from app.services import wechat

router = APIRouter()


@router.get("/wechats", response_model=WechatListResponse, dependencies=[Depends(check_permission('WechatList'))],
            summary="微信媒体平台列表")
def lists(params: SearchQuery = Depends()):
    return wechat.lists(params)


@router.get("/wechats/{id}", response_model=WechatItem, dependencies=[Depends(check_permission('WechatList'))],
            summary="微信媒体平台详情", )
def detail(id: int):
    item = wechat.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="微信媒体平台不存在")
    return item


@router.post("/wechats", response_model=ResponseSuccess, dependencies=[Depends(check_permission('WechatList'))],
             summary="添加微信媒体平台")
def add(params: WechatForm):
    try:
        wechat.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加微信媒体平台失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加微信媒体平台失败')


@router.put("/wechats/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('WechatList'))],
            summary="编辑微信媒体平台")
def update(id: int, params: WechatForm):
    try:
        wechat.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑微信媒体平台失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑微信媒体平台失败')


@router.delete("/wechats/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('WechatList'))],
               summary="删除微信媒体平台")
def delete(id: int):
    try:
        wechat.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除微信媒体平台失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除微信媒体平台失败')


@router.post("/wechats/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('WechatList'))], summary="重建微信媒体平台缓存")
def rebuild_cache():
    try:
        wechat.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建微信媒体平台缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建微信媒体平台缓存失败')
