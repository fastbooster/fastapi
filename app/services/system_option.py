#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 22:55

import json

from sqlalchemy.sql.expression import desc

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.system_option import SystemOptionModel
from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD

from app.schemas.system_option import OptionItem, OptionSearchQuery, OptionListResponse


def safe_whitelist_fields(option_data: dict) -> dict:
    safe_fields = ['option_name', 'option_value']
    return {k: v for k, v in option_data.items() if k in safe_fields}


def get_option(id: int) -> SystemOptionModel | None:
    with get_session(read_only=True) as db:
        option = db.query(SystemOptionModel).filter(
            SystemOptionModel.id == id).first()

    if option is not None:
        return option

    return None


def get_option_from_cache(option_name: str) -> OptionItem:
    with get_redis() as redis:
        setting = redis.hget(REDIS_SYSTEM_OPTIONS_AUTOLOAD, option_name)
        setting = json.loads(setting) if setting else {
            "option_name": option_name, "option_value": None}
    return setting


def get_option_by_name(option_name: str) -> SystemOptionModel | None:
    with get_session(read_only=True) as db:
        option = db.query(SystemOptionModel).filter(
            SystemOptionModel.option_name == option_name).first()

    if option is not None:
        return option

    return None


def get_option_list(params: OptionSearchQuery) -> OptionListResponse:
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
        if params.locked in ("yes", "no"):
            lock = 1 if params.locked == "yes" else 0
            query = query.filter(SystemOptionModel.lock == lock)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def add_option(params: OptionItem) -> None:
    with get_session() as db:
        exists_count = db.query(SystemOptionModel).filter(
            SystemOptionModel.option_name == params.option_name).count()
        if exists_count > 0:
            raise ValueError('该选项名称已存在')

        option_model = SystemOptionModel(
            option_name=params.option_name,
            option_value=params.option_value,
            richtext=params.richtext,
            position=params.position,
            autoload=params.autoload,
            lock=params.lock,
            memo=params.memo,
        )

        db.add(option_model)
        db.commit()
        update_cache(option_model)


def edit_option(params: OptionItem) -> None:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(
            id=params.id).first()
        if option_model is None:
            raise ValueError(f'选项不存在(id={params.id})')

        exists_count = db.query(SystemOptionModel).filter(SystemOptionModel.option_name == params.option_name,
                                                          SystemOptionModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError('该选项名称已存在')

        # 如果option_model.autoload为1，params.autoload为0，需要清除缓存
        if option_model.autoload == 1 and params.autoload == 0:
            update_cache(option_model, is_delete=True)

        # 禁止修改 option_name, 防止缓存溢出
        # option_model.option_name = params.option_name
        option_model.option_value = params.option_value
        option_model.richtext = params.richtext
        option_model.position = params.position
        option_model.autoload = params.autoload
        option_model.lock = params.lock
        option_model.memo = params.memo

        db.commit()
        update_cache(option_model)


def delete_option(id: int) -> None:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(id=id).first()
        if option_model is None:
            raise ValueError(f'选项不存在(id={id})')
        if option_model.lock:
            raise ValueError(f'选项已锁定，不能删除')

        db.delete(option_model)
        db.commit()
        update_cache(option_model, is_delete=True)


def autoupdate(params: OptionItem) -> None:
    '''不存在则插入数据，否则更新选项值'''
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(
            option_name=params.option_name).first()
        if option_model is None:
            option_model = SystemOptionModel(**params.__dict__)
            db.add(option_model)
        else:
            option_model.option_value = params.option_value

        db.commit()

        # 事物提交后 option_model 会被情况，重新查询
        option_model = db.query(SystemOptionModel).filter_by(
            option_name=params.option_name).first()
        update_cache(option_model)


def update_cache(option_model: SystemOptionModel, is_delete: bool = False) -> None:
    if option_model.autoload == 1:
        with get_redis() as redis:
            if is_delete:
                redis.hdel(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           option_model.option_name)
            else:
                redis.hset(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           option_model.option_name, option_model.option_value)


def rebuild_cache() -> None:
    with get_session(read_only=True) as db:
        with get_redis() as redis:
            redis.delete(REDIS_SYSTEM_OPTIONS_AUTOLOAD)
            items = db.query(SystemOptionModel).filter_by(autoload=1).all()
            for item in items:
                redis.hset(REDIS_SYSTEM_OPTIONS_AUTOLOAD,
                           item.option_name, item.option_value)
