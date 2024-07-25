#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/25 17:36

import json
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.core.redis import get_redis

from app.constants.constants import REDIS_WECHAT

from app.models.wechat import WechatModel
from app.schemas.schemas import StatusType, MysqlBoolType
from app.schemas.wechat import WechatType, WechatItem, WechatSearchQuery, WechatListResponse


def get_wechat(id: int) -> WechatModel | None:
    with get_session(read_only=True) as db:
        item = db.query(WechatModel).filter(
            WechatModel.id == id).first()
        if item is not None:
            return item
        return None


def get_wechat_list(params: WechatSearchQuery) -> WechatListResponse:
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
            query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add_wechat(params: WechatItem) -> None:
    with get_session() as db:
        exists_count = db.query(WechatModel).filter(
            WechatModel.appid == params.appid).count()
        if exists_count > 0:
            raise ValueError('appid已存在')

        fields = params.model_dump()
        fields.pop('id')
        fields.pop('created_at')
        fields.pop('updated_at')
        fields['status'] = params.status.value
        fields['type'] = params.type.value
        model = WechatModel(**fields)
        db.add(model)
        db.commit()

        fields['id'] = model.id
        fields['created_at'] = model.created_at
        fields['updated_at'] = model.updated_at
        update_cache(fields)


def edit_wechat(params: WechatItem) -> None:
    with get_session() as db:
        model = db.query(WechatModel).filter_by(
            id=params.id).first()
        if model is None:
            raise ValueError(f'微信媒体平台不存在(id={params.id})')

        exists_count = db.query(WechatModel).filter(
            WechatModel.appid == params.appid, WechatModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError('appid已存在')

        # 禁止修改 appid 防止缓存溢出
        fields = params.model_dump()
        fields.pop('appid')
        fields.pop('id')
        fields.pop('created_at')
        fields.pop('updated_at')
        fields['status'] = params.status.value
        fields['type'] = params.type.value

        model.from_dict(fields)
        db.commit()

        fields['appid'] = model.appid
        fields['created_at'] = model.created_at
        fields['updated_at'] = model.updated_at
        update_cache(fields)


def delete_wechat(id: int) -> None:
    with get_session() as db:
        model = db.query(WechatModel).filter_by(id=id).first()
        if model is None:
            raise ValueError(f'微信媒体平台不存在(id={id})')
        params = model.to_dict()
        db.delete(model)
        db.commit()
        update_cache(params, is_delete=True)


def update_cache(params: dict, is_delete: bool = False) -> None:
    '''注意：模型的 appid 字堵不能修改，否则在删除时无法清理缓存，可能缓存会溢出'''
    if isinstance(params["type"], WechatType):
        params["type"] = params["type"].value
    if isinstance(params["status"], StatusType):
        params["status"] = params["status"].value
    if isinstance(params["created_at"], datetime):
        params["created_at"] = params["created_at"].isoformat()
    if isinstance(params["updated_at"], datetime):
        params["updated_at"] = params["updated_at"].isoformat()
    with get_redis() as redis:
        if is_delete == False:
            redis.hset(REDIS_WECHAT, params["appid"], json.dumps(params))
        else:
            redis.hdel(REDIS_WECHAT, params["appid"])


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        with get_redis() as redis:
            items = db.query(WechatModel).order_by(asc('id')).all()
            redis.delete(REDIS_WECHAT)
            for item in items:
                params = item.__dict__
                params.pop("_sa_instance_state")
                if isinstance(params["type"], WechatType):
                    params["type"] = params["type"].value
                if isinstance(params["status"], StatusType):
                    params["status"] = params["status"].value
                if isinstance(params["created_at"], datetime):
                    params["created_at"] = params["created_at"].isoformat()
                if isinstance(params["updated_at"], datetime):
                    params["updated_at"] = params["updated_at"].isoformat()
                redis.hset(REDIS_WECHAT, params["appid"], json.dumps(params))
