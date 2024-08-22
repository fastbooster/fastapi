#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post.py
# Author: FastBooster Generator
# Time: 2024-08-22 14:18


from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session
from app.models.cms import PostModel
from app.schemas.post import PostForm, SearchQuery
from app.schemas.schemas import StatusType


def get(id: int) -> PostModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(PostModel).filter(PostModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(PostModel).order_by(desc('id'))
        if isinstance(params.id, int):
            query = query.filter_by(id=params.id)
        if isinstance(params.pid, int):
            query = query.filter_by(pid=params.pid)
        if isinstance(params.category_id, int):
            query = query.filter_by(category_id=params.category_id)
        if isinstance(params.user_id, int):
            query = query.filter_by(user_id=params.user_id)
        if params.title:
            query = query.filter(PostModel.title.like(f'%{params.title}%'))
        if params.keywords:
            query = query.filter(PostModel.keywords.like(f'%{params.keywords}%'))
        if isinstance(params.status, StatusType):
            query = query.filter_by(status=params.status.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: PostForm) -> None:
    with get_session() as db:
        current_model = PostModel()
        current_model.from_dict(params.__dict__)
        if isinstance(params.comment_status, StatusType):
            current_model.comment_status = params.comment_status.value
        if isinstance(params.status, StatusType):
            current_model.status = params.status.value

        db.add(current_model)
        db.commit()
        db.refresh(current_model)


def update(id: int, params: PostForm) -> None:
    with get_session() as db:
        current_model = db.query(PostModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'文章不存在(id={id})')

        current_model.from_dict(params.__dict__)
        if isinstance(params.comment_status, StatusType):
            current_model.comment_status = params.comment_status.value
        if isinstance(params.status, StatusType):
            current_model.status = params.status.value

        db.commit()


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(PostModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'文章不存在(id={id})')
        db.delete(current_model)
        db.commit()
