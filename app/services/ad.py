#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: ad.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/29 17:18

import json
import operator

from sqlalchemy.sql.expression import asc, desc

from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.cms import AdSpaceModel, AdModel
from app.constants.constants import REDIS_AD_PREFIX
from app.schemas.ad import SpaceSearchQuery, SpaceAddForm, SpaceEditForm, AdSearchQuery, AdAddForm, AdEditForm


def safe_whitelist_fields(ad_data: dict) -> dict:
    safe_fields = ['position', 'title', 'subtitle', 'description', 'content', 'pc_cover', 'mobile_cover',
                   'button_title', 'button_url']
    return {k: v for k, v in ad_data.items() if k in safe_fields}


def get_space_list(params: SpaceSearchQuery) -> list[AdSpaceModel]:
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(AdSpaceModel).order_by(desc('id'))
        if params.id > 0:
            query = query.filter_by(id=params.id)
        if params.name:
            query = query.filter(AdSpaceModel.name.like(f'%{params.name}%'))
        if params.status > -1:
            query = query.filter_by(status=params.status)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)
        return query.all()


def get_space(id: int) -> AdSpaceModel | None:
    with get_session(read_only=True) as db:
        space = db.query(AdSpaceModel).filter(AdSpaceModel.id == id).first()
        if space is not None:
            return space
        return None


def add_space(params: SpaceAddForm) -> None:
    with get_session() as db:
        space_model = AdSpaceModel(
            name=params.name,
            width=params.width,
            height=params.height,
            status=params.status,
        )
        db.add(space_model)
        db.commit()


def edit_space(params: SpaceEditForm) -> None:
    with get_session() as db:
        space_model = db.query(AdSpaceModel).filter_by(id=params.id).first()
        if space_model is None:
            raise ValueError(f'广告位不存在(id={params.id})')

        space_model.name = params.name
        space_model.width = params.width
        space_model.height = params.height
        space_model.status = params.status

        db.commit()


def delete_space(id: int) -> None:
    with get_session() as db:
        space_model = db.query(AdSpaceModel).filter_by(id=id).first()
        if space_model is None:
            raise ValueError(f'广告位不存在(id={id})')

        exists_count = db.query(AdModel).filter(AdModel.space_id == id).count()
        if exists_count > 0:
            raise ValueError('请先清除广告资源')

        db.delete(space_model)
        db.commit()

    with get_redis() as redis:
        redis.delete(REDIS_AD_PREFIX + str(id))


def get_ad_list(params: AdSearchQuery) -> list[AdModel]:
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(AdModel).order_by(asc('asc_sort_order'), desc('id'))
        if params.id > 0:
            query = query.filter_by(id=params.id)
        if params.space_id > 0:
            query = query.filter_by(space_id=params.space_id)
        if params.status > -1:
            query = query.filter_by(status=params.status)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)
        return query.all()


def get_ad_list_from_cache(space_id: int) -> list:
    data = []
    with get_redis() as redis:
        items = redis.hgetall(REDIS_AD_PREFIX + str(space_id))
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


def get_ad(id: int) -> AdModel | None:
    with get_session(read_only=True) as db:
        ad = db.query(AdModel).filter(AdModel.id == id).first()
        if ad is not None:
            return ad
        return None


def add_ad(params: AdAddForm) -> None:
    with get_session() as db:
        space_model = db.query(AdSpaceModel).filter_by(
            id=params.space_id).first()
        if space_model is None:
            raise ValueError(f'广告位不存在(id={params.space_id})')

        ad_model = AdModel()
        for attr, value in params.__dict__.items():
            if hasattr(ad_model, attr):
                value = params.position.value if attr == 'position' else value
                setattr(ad_model, attr, value)

        db.add(ad_model)
        db.commit()
        update_cache(ad_model)


def edit_ad(params: AdEditForm) -> None:
    with get_session() as db:
        ad_model = db.query(AdModel).filter_by(id=params.id).first()
        if ad_model is None:
            raise ValueError(f'广告不存在(id={params.id})')

        if ad_model.space_id != params.space_id:
            space_model = db.query(AdSpaceModel).filter_by(
                id=params.space_id).first()
            if space_model is None:
                raise ValueError(f'广告位不存在(id={params.space_id})')

        for attr, value in params.__dict__.items():
            if hasattr(ad_model, attr):
                value = params.position.value if attr == 'position' else value
                setattr(ad_model, attr, value)

        db.commit()
        update_cache(ad_model)


def delete_ad(id: int) -> None:
    with get_session() as db:
        ad_model = db.query(AdModel).filter_by(id=id).first()
        if ad_model is None:
            raise ValueError(f'广告不存在(id={id})')

        db.delete(ad_model)
        db.commit()
        update_cache(ad_model, is_delete=True)


def rebuild_cache() -> None:
    with get_redis() as redis:
        keys = redis.keys(REDIS_AD_PREFIX + '*')
        if keys:
            redis.delete(*keys)
    with get_session(read_only=True) as db:
        ads = db.query(AdModel).order_by(asc('id')).all()
        if ads:
            for ad in ads:
                update_cache(ad)


def update_cache(ad: AdModel, is_delete: bool = False) -> None:
    with get_redis() as redis:
        if is_delete or ad.status == 0:
            redis.hdel(REDIS_AD_PREFIX + str(ad.space_id), ad.id)
        else:
            redis.hset(REDIS_AD_PREFIX + str(ad.space_id), ad.id,
                       json.dumps(ad.__dict__, default=str))
