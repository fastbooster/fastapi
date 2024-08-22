#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post.py
# Author: FastBooster Generator
# Time: 2024-08-22 14:18

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.post import PostForm, PostItem, SearchQuery, PostListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import post

router = APIRouter()


@router.get("/posts", response_model=PostListResponse, dependencies=[Depends(check_permission('PostList'))],
            summary="文章列表")
def lists(params: SearchQuery = Depends()):
    return post.lists(params)


@router.get("/posts/{id}", response_model=PostItem, dependencies=[Depends(check_permission('PostList'))],
            summary="文章详情", )
def detail(id: int):
    current_model = post.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="文章不存在")
    return current_model


@router.post("/posts", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))],
             summary="添加文章")
def add(params: PostForm):
    try:
        post.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加文章失败')


@router.put("/posts/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))],
            summary="编辑文章")
def update(id: int, params: PostForm):
    try:
        post.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑文章失败')


@router.delete("/posts/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))],
               summary="删除文章")
def delete(id: int):
    try:
        post.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除文章失败')
