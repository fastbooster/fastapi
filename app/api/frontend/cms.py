#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: cms.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/27 11:39

from loguru import logger

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
