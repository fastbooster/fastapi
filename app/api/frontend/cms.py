#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: cms.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/27 11:39

from app.core.log import logger

from fastapi import APIRouter, HTTPException, Depends

from app.core.security import check_permission
from app.services import post_category as CategoryService, post as PostService

from app.schemas.post_category import CategorySearchQuery, CategoryAddForm, CategoryEditForm
from app.schemas.post import PostSearchQuery, PostAddForm, PostEditForm
from app.constants.constants import RESPONSE_OK

router = APIRouter()


@router.get('/post_category', summary='文章分类列表')
def category_list():
    items = CategoryService.get_category_list_from_cache()
    return [CategoryService.safe_whitelist_fields(item) for item in items]


@router.get("/post", summary="文章列表")
def post_list(params: PostSearchQuery = Depends()):
    return PostService.get_post_list_frontend(params)


@router.get("/post/{id}", summary="文章详情", )
def post_detail(id: int):
    post = PostService.get_post_frontend(id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post
