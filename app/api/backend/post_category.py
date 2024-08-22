#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: FastBooster Generator
# Time: 2024-08-22 15:32

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.schemas.post_category import PostCategoryForm, PostCategoryItem, SearchQuery, PostCategoryListResponse
from app.schemas.schemas import ResponseSuccess
from app.services import post_category

router = APIRouter()


@router.get("/post_categories", response_model=PostCategoryListResponse,
            dependencies=[Depends(check_permission('PostCategoryList'))], summary="文章分类列表")
def lists(params: SearchQuery = Depends()):
    return post_category.lists(params)


@router.get("/post_categories/{id}", response_model=PostCategoryItem,
            dependencies=[Depends(check_permission('PostCategoryList'))],
            summary="文章分类详情", )
def detail(id: int):
    current_model = post_category.get(id)
    if not current_model:
        raise HTTPException(status_code=404, detail="文章分类不存在")
    return current_model


@router.post("/post_categories", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PostCategoryList'))], summary="添加文章分类")
def add(params: PostCategoryForm):
    try:
        post_category.add(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加文章分类失败')


@router.put("/post_categories/{id}", response_model=ResponseSuccess,
            dependencies=[Depends(check_permission('PostCategoryList'))], summary="编辑文章分类")
def update(id: int, params: PostCategoryForm):
    try:
        post_category.update(id, params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑文章分类失败')


@router.delete("/post_categories/{id}", response_model=ResponseSuccess,
               dependencies=[Depends(check_permission('PostCategoryList'))], summary="删除文章分类")
def delete(id: int):
    try:
        post_category.delete(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除文章分类失败')


@router.post("/post_categories/rebuild_cache", response_model=ResponseSuccess,
             dependencies=[Depends(check_permission('PostCategoryList'))], summary="重建文章分类缓存")
def rebuild_cache():
    try:
        post_category.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建文章分类缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建文章分类缓存失败')
