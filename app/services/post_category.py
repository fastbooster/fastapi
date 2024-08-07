#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 17:05

import json
import operator

from sqlalchemy.sql.expression import asc, desc
from pydantic import BaseModel

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.cms import PostCategoryModel
from app.constants.constants import REDIS_POST_CATEGORY
from app.schemas.post_category import CategorySearchQuery, CategoryAddForm, CategoryEditForm


def safe_whitelist_fields(post_category_data: dict) -> dict:
    safe_fields = ['id', 'name', 'alias']
    return {k: v for k, v in post_category_data.items() if k in safe_fields}


def get_category(id: int) -> PostCategoryModel | None:
    with get_session(read_only=True) as db:
        post_category = db.query(PostCategoryModel).filter(
            PostCategoryModel.id == id).first()

    if post_category is not None:
        return post_category

    return None


def get_category_list(params: CategorySearchQuery) -> list[PostCategoryModel]:
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(PostCategoryModel).order_by(desc('id'))
        if params.name:
            query = query.filter(
                PostCategoryModel.name.like(f'%{params.name}%'))
        if params.alias:
            query = query.filter(
                PostCategoryModel.alias.like(f'%{params.alias}%'))
        if params.keywords:
            query = query.filter(
                PostCategoryModel.keywords.like(f'%{params.keywords}%'))
        if not export:
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return query.all()


def get_category_list_from_cache() -> list:
    data = []
    with get_redis() as redis:
        items = redis.hgetall(REDIS_POST_CATEGORY)
        # 转换为JSON格式并过滤掉status=0的条目
        filtered_items = []
        print(type(filtered_items))
        for key, value in items.items():
            item = json.loads(value)
            if item.get('status', 0) != 0:
                filtered_items.append(item)

        # 按asc_sort_order字段进行排序
        data = sorted(filtered_items,
                      key=operator.itemgetter('asc_sort_order'))

    return data


def add_category(params: CategoryAddForm) -> None:
    with get_session() as db:
        data_validate(params)

        post_category_model = PostCategoryModel(
            name=params.name,
            alias=params.alias,
            keywords=params.keywords,
            asc_sort_order=params.asc_sort_order,
            status=params.status,
        )

        db.add(post_category_model)
        db.commit()
        update_cache(post_category_model)


def edit_category(params: CategoryEditForm) -> None:
    with get_session() as db:
        post_category_model = db.query(
            PostCategoryModel).filter_by(id=params.id).first()
        if post_category_model is None:
            raise ValueError(f'分类不存在(id={params.id})')

        data_validate(params)

        post_category_model.name = params.name
        post_category_model.alias = params.alias
        post_category_model.keywords = params.keywords
        post_category_model.asc_sort_order = params.asc_sort_order
        post_category_model.status = params.status

        db.commit()
        update_cache(post_category_model)


def delete_category(id: int) -> None:
    with get_session() as db:
        post_category_model = db.query(
            PostCategoryModel).filter_by(id=id).first()
        if post_category_model is None:
            raise ValueError(f'分类不存在(id={id})')

        db.delete(post_category_model)
        db.commit()
        update_cache(post_category_model, is_delete=True)


def rebuild_cache() -> None:
    with get_redis() as redis:
        redis.delete(REDIS_POST_CATEGORY)
    with get_session(read_only=True) as db:
        post_category_models = db.query(
            PostCategoryModel).order_by(asc('id')).all()
        if post_category_models:
            for post_category_model in post_category_models:
                update_cache(post_category_model)


def update_cache(post_category_model: PostCategoryModel, is_delete: bool = False) -> None:
    with get_redis() as redis:
        if is_delete:
            redis.hdel(REDIS_POST_CATEGORY, post_category_model.id)
        else:
            redis.hset(REDIS_POST_CATEGORY, post_category_model.id,
                       json.dumps(post_category_model.__dict__, default=str))


def data_validate(params: BaseModel) -> bool:
    with get_session(read_only=True) as db:
        id = params.id if hasattr(params, 'id') else 0
        name = params.name
        alias = params.alias

        # 查询是否存在同名分类（排除自身）
        existing_name_category = db.query(PostCategoryModel).filter(PostCategoryModel.name == name,
                                                                    PostCategoryModel.id != id).first()
        if existing_name_category is not None:
            raise ValueError(f'名称已存在(name={name})')

        # 查询是否存在同别名分类（排除自身）
        existing_alias_category = db.query(PostCategoryModel).filter(PostCategoryModel.alias == alias,
                                                                     PostCategoryModel.id != id).first()
        if existing_alias_category is not None:
            raise ValueError(f'别名已存在(alias={alias})')

    return True
