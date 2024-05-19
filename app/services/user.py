#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 16:50

import secrets

from sqlalchemy.sql.expression import asc, desc, or_

from app.core.security import encode_password
from app.core.mysql import get_session
from app.models.user import UserModel

from app.schemas.user import UserSearchQuery, UserAddForm


def get_user(id: int) -> UserModel | None:
    with get_session() as db:
        user = db.query(UserModel).filter(UserModel.id == id).first()

    if user is not None:
        return user

    return None


def get_user_list(params: UserSearchQuery) -> list[UserModel]:
    export = True if params.export == 1 else False
    with get_session() as db:
        query = db.query(UserModel).order_by(desc('id'))
        if params.phone:
            query = query.filter(UserModel.phone.like(f'%{params.phone}%'))
        if params.email:
            query = query.filter(UserModel.email.like(f'%{params.email}%'))
        if params.pid != -1:
            query = query.filter_by(pid=params.pid)
        if params.role_id != -1:
            query = query.filter_by(role_id=params.role_id)
        if params.status != -1:
            query = query.filter_by(status=params.status)
        if not export:
            offset = (params.page - 1) * params.size
            query.offset(offset).limit(params.size)

    return query.all()


def add_user(params: UserAddForm) -> bool:
    if params.phone is None and params.email is None:
        raise ValueError('手机或邮箱至少填写一项')

    with get_session() as db:
        exists_count = db.query(UserModel).filter(
            or_(UserModel.phone == params.phone, UserModel.email == params.email)).count()
        if exists_count > 0:
            raise ValueError('手机或邮箱已存在')

        password_salt = secrets.token_urlsafe(32)
        password_hash = encode_password(params.password, password_salt)
        user_model = UserModel(
            phone=params.phone,
            email=params.email,
            nickname=params.nickname,
            password_salt=password_salt,
            password_hash=password_hash,
            role_id=params.role_id,
            gender=params.gender.value,
        )

        db.add(user_model)
        db.commit()
    return True


def safe_whitelist_fields(user_data: dict) -> dict:
    safe_fields = ['id', 'phone_code', 'phone', 'email', 'nickname', 'gender', 'avatar',
                   'promotion_code', 'wechat_openid', 'wechat_unionid'
                   'join_ip', 'join_at']
    return {k: v for k, v in user_data.items() if k in safe_fields}
