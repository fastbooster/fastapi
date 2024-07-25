#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 16:35

import traceback

from fastapi import APIRouter, HTTPException, Depends

from app.core.log import logger
from app.core.security import check_permission
from app.services import post_category as CategoryService, post as PostService

from app.schemas.schemas import ResponseSuccess
from app.schemas.post_category import CategorySearchQuery, CategoryAddForm, CategoryEditForm
from app.schemas.post import PostSearchQuery, PostAddForm, PostEditForm

router = APIRouter()


@router.get("/post_category", dependencies=[Depends(check_permission('PostCategoryList'))], summary="文章分类列表")
def category_list(params: CategorySearchQuery = Depends()):
    return CategoryService.get_category_list(params)


@router.get("/post_category/{id}", dependencies=[Depends(check_permission('PostCategoryList'))], summary="文章分类详情",)
def category_detail(id: int):
    post_category = CategoryService.get_category(id)
    if not post_category:
        raise HTTPException(status_code=404, detail="文章分类不存在")
    return post_category


@router.post("/post_category", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostCategoryList'))], summary="添加文章分类")
def add_category(params: CategoryAddForm):
    try:
        CategoryService.add_category(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加文章分类失败')


@router.patch("/post_category", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostCategoryList'))], summary="编辑文章分类")
def edit_category(params: CategoryEditForm):
    try:
        CategoryService.edit_category(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑文章分类失败')


@router.delete("/post_category/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostCategoryList'))], summary="删除文章分类",)
def delete_category(id: int):
    try:
        CategoryService.delete_category(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除文章分类失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除文章分类失败')


@router.post("/post_category/rebuild_cache", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostCategoryList'))], summary="重建文章分类缓存",)
def rebuild_cache():
    try:
        CategoryService.rebuild_cache()
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'重建文章分类缓存失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='重建文章分类缓存失败')


@router.get("/post", dependencies=[Depends(check_permission('PostList'))], summary="文章列表")
def post_list(params: PostSearchQuery = Depends()):
    return PostService.get_post_list(params)


@router.get("/post/{id}", dependencies=[Depends(check_permission('PostList'))], summary="文章详情",)
def post_detail(id: int):
    post = PostService.get_post(id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


@router.post("/post", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))], summary="添加文章")
def add_post(params: PostAddForm):
    try:
        PostService.add_post(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'添加文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='添加文章失败')


@router.patch("/post", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))], summary="编辑文章")
def edit_post(params: PostEditForm):
    try:
        PostService.edit_post(params)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'编辑文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='编辑文章失败')


@router.delete("/post/{id}", response_model=ResponseSuccess, dependencies=[Depends(check_permission('PostList'))], summary="删除文章",)
def delete_post(id: int):
    try:
        PostService.delete_post(id)
        return ResponseSuccess()
    except ValueError as e:
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'删除文章失败：{e}')
        logger.info(f'调用堆栈：{traceback.format_exc()}')
        raise HTTPException(status_code=500, detail='删除文章失败')
