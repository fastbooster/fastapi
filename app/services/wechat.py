#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/25 17:36

import json

from sqlalchemy.sql.expression import asc, desc

from app.constants.constants import REDIS_WECHAT
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.wechat import WechatModel
from app.schemas.schemas import StatusType
from app.schemas.wechat import WechatType, WechatForm, SearchQuery
from app.utils.helper import serialize_datetime


def get(id: int) -> WechatModel | None:
    with get_session(read_only=True) as db:
        item = db.query(WechatModel).filter(
            WechatModel.id == id).first()
        if item is not None:
            return item
        return None


def lists(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(WechatModel).order_by(desc('id'))
        if params.appid:
            query = query.filter(
                WechatModel.appid.like(f'%{params.appid}%'))
        if params.appname:
            query = query.filter(
                WechatModel.appname.like(f'%{params.appname}%'))
        if isinstance(params.type, WechatType):
            query = query.filter(
                WechatModel.type == params.type.value)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add(params: WechatForm) -> None:
    with get_session() as db:
        exists_count = db.query(WechatModel).filter(
            WechatModel.appid == params.appid).count()
        if exists_count > 0:
            raise ValueError('appid已存在')

        if isinstance(params.type, WechatType):
            params.type = params.type.value
        if isinstance(params.status, StatusType):
            params.status = params.status.value

        current_model = WechatModel()
        current_model.from_dict(params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update(id: int, params: WechatForm) -> None:
    with get_session() as db:
        current_model = db.query(WechatModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'微信媒体平台不存在(id={id})')

        # exists_count = db.query(WechatModel).filter(WechatModel.appid == params.appid, WechatModel.id != id).count()
        # if exists_count > 0:
        #     raise ValueError('appid已存在')

        if isinstance(params.type, WechatType):
            params.type = params.type.value
        if isinstance(params.status, StatusType):
            params.status = params.status.value

        # 禁止修改 appid 防止缓存溢出
        old_appid = current_model.appid
        current_model.from_dict(params.__dict__)
        current_model.appid = old_appid

        db.commit()
        db.refresh(current_model)

        update_cache(current_model)


def delete(id: int) -> None:
    with get_session() as db:
        current_model = db.query(WechatModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'微信媒体平台不存在(id={id})')
        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def update_cache(current_model: WechatModel, is_delete: bool = False) -> None:
    """注意：修改模型时候 appid 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出"""
    with get_redis() as redis:
        if not is_delete:
            params = current_model.to_dict()
            params['created_at'] = serialize_datetime(params['created_at'])
            params['updated_at'] = serialize_datetime(params['updated_at'])
            redis.hset(REDIS_WECHAT, current_model.appid, json.dumps(params))
        else:
            redis.hdel(REDIS_WECHAT, current_model.appid)


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        items = db.query(WechatModel).order_by(asc('id')).all()
        with get_redis() as redis:
            redis.delete(REDIS_WECHAT)
            for current_model in items:
                update_cache(current_model)
