#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 22:55

import secrets

from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.system_option import SystemOptionModel
from app.constants.constants import REDIS_SYSTEM_OPTIONS_AUTOLOAD

from app.schemas.system_option import OptionSearchQuery, OptionAddForm, OptionEditForm


def safe_whitelist_fields(option_data: dict) -> dict:
    safe_fields = ['id', 'option_name', 'option_value', 'richtext', 'position']
    return {k: v for k, v in option_data.items() if k in safe_fields}


def get_option(id: int) -> SystemOptionModel | None:
    with get_session() as db:
        option = db.query(SystemOptionModel).filter(SystemOptionModel.id == id).first()

    if option is not None:
        return option

    return None


def get_option_list(params: OptionSearchQuery) -> list[SystemOptionModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(SystemOptionModel).order_by(desc('id'))
        if params.option_name:
            query = query.filter(SystemOptionModel.option_name.like(f'%{params.option_name}%'))
        if params.memo:
            query = query.filter(SystemOptionModel.memo.like(f'%{params.memo}%'))
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def add_option(params: OptionAddForm) -> bool:
    with get_session() as db:
        exists_count = db.query(SystemOptionModel).filter(SystemOptionModel.option_name == params.option_name).count()
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
        updateCache(option_model)
    return True


def edit_option(params: OptionEditForm) -> bool:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(id=params.id).first()
        if option_model is None:
            raise ValueError(f'选项不存在(id={params.id})')

        exists_count = db.query(SystemOptionModel).filter(SystemOptionModel.option_name == params.option_name, SystemOptionModel.id != params.id).count()
        if exists_count > 0:
            raise ValueError('该选项名称已存在')

        # 如果option_model.autoload为1，params.autoload为0，需要清除缓存
        if option_model.autoload == 1 and params.autoload == 0:
            updateCache(option_model, is_delete=True)

        option_model.option_name = params.option_name
        option_model.option_value = params.option_value
        option_model.richtext = params.richtext
        option_model.position = params.position
        option_model.autoload = params.autoload
        option_model.lock = params.lock
        option_model.memo = params.memo

        db.commit()
        updateCache(option_model)
    return True


def delete_option(id: int) -> bool:
    with get_session() as db:
        option_model = db.query(SystemOptionModel).filter_by(id=id).first()
        if option_model is None:
            raise ValueError(f'选项不存在(id={id})')
        if option_model.lock:
            raise ValueError(f'选项已锁定，不能删除')

        db.delete(option_model)
        db.commit()
        updateCache(option_model, is_delete=True)
    return True


def rebuild_cache() -> bool:
    with get_redis() as redis:
        redis.delete(REDIS_SYSTEM_OPTIONS_AUTOLOAD)
    with get_session() as db:
        option_models = db.query(SystemOptionModel).filter_by(autoload=1).order_by(asc('id')).all()
        if option_models:
            for option_model in option_models:
                updateCache(option_model)
    return True

def updateCache(option_model: SystemOptionModel, is_delete: bool = False) -> None:
    if option_model.autoload == 1:
        with get_redis() as redis:
            if is_delete:
                redis.hdel(REDIS_SYSTEM_OPTIONS_AUTOLOAD, option_model.option_name)
            else:
                redis.hset(REDIS_SYSTEM_OPTIONS_AUTOLOAD, option_model.option_name, option_model.option_value)
