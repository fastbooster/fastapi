#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 22:55

import json

from sqlalchemy.sql.expression import desc

from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.system_option import SystemOptionModel
from app.schemas.system_option import SystemOptionForm, SystemOptionItem, SearchQuery


def get_option(id: int) -> SystemOptionModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(SystemOptionModel).filter(
            SystemOptionModel.id == id).first()
        if current_model is not None:
            return current_model
        return None


def get_option_from_cache(option_name: str) -> SystemOptionItem:
    with get_redis() as redis:
        current_model = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, option_name)
        current_model = json.loads(current_model) if current_model else {
            "option_name": option_name, "option_value": None}
        return current_model


def get_option_by_name(option_name: str) -> SystemOptionModel | None:
    with get_session(read_only=True) as db:
        current_model = db.query(SystemOptionModel).filter(
            SystemOptionModel.option_name == option_name).first()
        if current_model is not None:
            return current_model
        return None


def get_option_list(params: SearchQuery) -> dict:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(SystemOptionModel).order_by(desc('id'))
        if params.option_name:
            query = query.filter(
                SystemOptionModel.option_name.like(f'%{params.option_name}%'))
        if params.memo:
            query = query.filter(
                SystemOptionModel.memo.like(f'%{params.memo}%'))
        if params.locked in (0, 1):
            query = query.filter(SystemOptionModel.lock == params.locked)
        if params.public in (0, 1):
            query = query.filter(SystemOptionModel.public == params.public)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add_option(params: SystemOptionForm) -> None:
    with get_session() as db:
        exists_count = db.query(SystemOptionModel).filter(
            SystemOptionModel.option_name == params.option_name).count()
        if exists_count > 0:
            raise ValueError('该选项名称已存在')

        current_model = SystemOptionModel(**params.__dict__)
        db.add(current_model)
        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def edit_option(id: int, params: SystemOptionForm) -> None:
    with get_session() as db:
        current_model = db.query(SystemOptionModel).filter_by(
            id=id).first()
        if current_model is None:
            raise ValueError(f'选项不存在(id={id})')

        exists_count = db.query(SystemOptionModel).filter(SystemOptionModel.option_name == params.option_name,
                                                          SystemOptionModel.id != id).count()
        if exists_count > 0:
            raise ValueError('该选项名称已存在')

        if current_model.autoload == 1 and params.autoload == 0:
            update_cache(current_model, is_delete=True)

        # 禁止修改 option_name, 防止缓存溢出
        data_dict = params.__dict__
        data_dict.pop('option_name')
        current_model.from_dict(data_dict)

        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def delete_option(id: int) -> None:
    with get_session() as db:
        current_model = db.query(SystemOptionModel).filter_by(id=id).first()
        if current_model is None:
            raise ValueError(f'选项不存在(id={id})')
        if current_model.lock:
            raise ValueError(f'选项已锁定，不能删除')

        db.delete(current_model)
        db.commit()
        update_cache(current_model, is_delete=True)


def autoupdate(params: SystemOptionForm) -> None:
    """不存在则插入数据，否则更新选项值"""
    with get_session() as db:
        current_model = db.query(SystemOptionModel).filter_by(
            option_name=params.option_name).first()
        if current_model is None:
            current_model = SystemOptionModel(**params.__dict__)
            db.add(current_model)
        else:
            data_dict = params.__dict__
            data_dict.pop('option_name')
            current_model.from_dict(data_dict)

        db.commit()
        db.refresh(current_model)
        update_cache(current_model)


def update_cache(current_model: SystemOptionModel, is_delete: bool = False) -> None:
    if current_model.autoload == 1:
        with get_redis() as redis:
            if is_delete:
                redis.hdel(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           current_model.option_name)
            else:
                redis.hset(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           current_model.option_name, current_model.option_value)


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        with get_redis() as redis:
            redis.delete(REDIS_SYSTEM_OPTIONS_AUTOLOAD)
            items = db.query(SystemOptionModel).filter_by(autoload=1).all()
            for item in items:
                redis.hset(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           item.option_name, item.option_value)
