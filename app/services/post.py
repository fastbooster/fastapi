#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 10:15

from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.models.cms import PostModel, PostCategoryModel
from app.schemas.post import PostSearchQuery, PostAddForm, PostEditForm


def safe_whitelist_fields(post_data: dict) -> dict:
    safe_fields = ['id', 'pid', 'category_id', 'title', 'subtitle', 'keywords', 'digest', 'content', 'author', 'editor',
                   'source', 'source_url', 'hero_image_url', 'view_num', 'like_num', 'collect_num', 'comment_num',
                   'created_at']
    return {k: v for k, v in post_data.items() if k in safe_fields}


def get_post_list(params: PostSearchQuery) -> list[PostModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(PostModel).order_by(desc('id'))
        if params.title:
            query = query.filter(PostModel.title.like(f'%{params.title}%'))
        if params.id > 0:
            query = query.filter_by(id=params.id)
        if params.pid > -1:
            query = query.filter_by(pid=params.pid)
        if params.category_id > -1:
            query = query.filter_by(category_id=params.category_id)
        if params.user_id > -1:
            query = query.filter_by(user_id=params.user_id)
        if params.status > -1:
            query = query.filter_by(status=params.status)
        if params.keywords:
            query = query.filter(PostModel.keywords.like(f'%{params.keywords}%'))
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def get_post_list_frontend(params: PostSearchQuery) -> list[dict]:
    with get_session() as db:
        query = db.query(
            PostModel.id, PostModel.pid, PostModel.title, PostModel.subtitle, PostModel.keywords, PostModel.digest,
            PostModel.hero_image_url, PostModel.author, PostModel.view_num, PostModel.collect_num,
            PostModel.comment_num, PostModel.category_id, PostCategoryModel.name.label('category_name'),
            PostModel.created_at
        ).join(PostCategoryModel, PostModel.category_id == PostCategoryModel.id, isouter=True) \
            .filter(PostModel.status == 1) \
            .order_by(desc(PostModel.id))

        if params.title:
            query = query.filter(PostModel.title.like(f'%{params.title}%'))
        if params.id > 0:
            query = query.filter(PostModel.id == params.id)
        if params.pid > -1:
            query = query.filter(PostModel.pid == params.pid)
        if params.category_id > -1:
            query = query.filter(PostModel.category_id == params.category_id)
        if params.keywords:
            query = query.filter(PostModel.keywords.like(f'%{params.keywords}%'))

        offset = (params.page - 1) * params.size
        query = query.offset(offset).limit(params.size)
        results = query.all()

    post_list = [result._asdict() for result in results]
    return post_list


def get_post(id: int) -> PostModel | None:
    with get_session() as db:
        post = db.query(PostModel).filter(PostModel.id == id).first()

    if post is not None:
        return post

    return None


def get_post_frontend(id: int) -> dict | None:
    with get_session() as db:
        result = db.query(PostModel, PostCategoryModel.name) \
            .join(PostCategoryModel, PostModel.category_id == PostCategoryModel.id, isouter=True) \
            .filter(PostModel.status == 1) \
            .filter(PostModel.id == id).first()

    if result is not None:
        post = result[0].__dict__
        post = safe_whitelist_fields(post)
        post['category_name'] = result[1]
        return post

    return None


def add_post(params: PostAddForm) -> bool:
    with get_session() as db:
        post_model = PostModel(**params.__dict__)

        db.add(post_model)
        db.commit()
    return True


def edit_post(params: PostEditForm) -> bool:
    with get_session() as db:
        post_model = db.query(PostModel).filter_by(id=params.id).first()
        if post_model is None:
            raise ValueError(f'文章不存在(id={params.id})')

        for attr, value in params.__dict__.items():
            if hasattr(post_model, attr):
                setattr(post_model, attr, value)

        db.commit()
    return True


def delete_post(id: int) -> bool:
    with get_session() as db:
        post_model = db.query(PostModel).filter_by(id=id).first()
        if post_model is None:
            raise ValueError(f'文章不存在(id={id})')

        db.delete(post_model)
        db.commit()
    return True
