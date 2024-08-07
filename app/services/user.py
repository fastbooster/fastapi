#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 16:50

import time
import datetime
import secrets

from sqlalchemy.sql.expression import asc, desc, or_

from app.core.security import encode_password
from app.core.mysql import get_session
from app.models.user import UserModel

from app.schemas.user import GenderType, JoinFromType, UserSearchQuery, UserQuickSearchQuery, UserItem, UserListResponse, UserQuickListResponse


def safe_whitelist_fields(user_data: dict) -> dict:
    safe_fields = ['id', 'phone_code', 'phone', 'email', 'nickname', 'gender', 'avatar',
                   'promotion_code', 'wechat_openid', 'wechat_unionid'
                   'join_ip', 'join_at']
    return {k: v for k, v in user_data.items() if k in safe_fields}


def get_user(id: int) -> UserModel | None:
    with get_session(read_only=True) as db:
        user = db.query(UserModel).filter(UserModel.id == id).first()
        if user is not None:
            return user
        return None


def get_user_list(params: UserSearchQuery) -> UserListResponse:
    total = -1
    export = True if params.export == 1 else False
    with get_session(read_only=True) as db:
        query = db.query(UserModel).order_by(desc('id'))
        if params.nickname:
            query = query.filter(
                UserModel.nickname.like(f'%{params.nickname}%'))
        if params.phone:
            query = query.filter(UserModel.phone.like(f'%{params.phone}%'))
        if params.email:
            query = query.filter(UserModel.email.like(f'%{params.email}%'))
        if isinstance(params.id, int):
            query = query.filter_by(id=params.id)
        if isinstance(params.pid, int):
            query = query.filter_by(pid=params.pid)
        if isinstance(params.role_id, int):
            query = query.filter_by(role_id=params.role_id)
        if isinstance(params.status, int):
            query = query.filter_by(status=params.status)
        if not export:
            total = query.count()
            offset = (params.page - 1) * params.size
            query = query.offset(offset).limit(params.size)
        return {"total": total, "items": query.all()}


def get_user_quick_list(params: UserQuickSearchQuery) -> UserQuickListResponse:
    with get_session(read_only=True) as db:
        query = db.query(UserModel.id, UserModel.nickname, UserModel.phone,
                         UserModel.email).order_by(desc('id'))
        if params.keyword.isnumeric():
            query = query.filter(or_(
                UserModel.id == params.keyword,
                UserModel.phone.like(f'%{params.keyword}%')
            ))
        else:
            query = query.filter(
                UserModel.nickname.like(f'%{params.keyword}%'))
        query.offset(0).limit(params.limit)
        items = query.all()
        return {"total": len(items), "items": items}


def add_user(params: UserItem) -> None:
    if not params.phone and not params.email:
        raise ValueError('手机或邮箱至少填写一项')

    with get_session() as db:
        if params.phone is not None:
            exists_count = db.query(UserModel).filter(
                UserModel.phone == params.phone).count()
            if exists_count > 0:
                raise ValueError('手机已存在')
        if params.email is not None:
            exists_count = db.query(UserModel).filter(
                UserModel.email == params.email).count()
            if exists_count > 0:
                raise ValueError('邮箱已存在')

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
            join_from=params.join_from.value,
            join_ip=params.join_ip,
        )

        db.add(user_model)
        db.commit()


def edit_user(params: UserItem) -> None:
    with get_session() as db:
        user_model = db.query(UserModel).filter_by(id=params.id).first()
        if user_model is None:
            raise ValueError(f'用户不存在(id={params.id})')

        if params.phone:
            exists_count = db.query(UserModel).filter(
                UserModel.id != user_model.id, UserModel.phone == params.phone).count()
            if exists_count > 0:
                raise ValueError('手机已存在')
            user_model.phone = params.phone
        if params.email:
            exists_count = db.query(UserModel).filter(
                UserModel.id != user_model.id, UserModel.email == params.email).count()
            if exists_count > 0:
                raise ValueError('邮箱已存在')
            user_model.email = params.email
        if params.nickname is not None:
            user_model.nickname = params.nickname
        if params.password is not None:
            user_model.password_salt = secrets.token_urlsafe(32)
            user_model.password_hash = encode_password(
                params.password, user_model.password_salt)
        if params.gender is not None:
            user_model.gender = params.gender.value
        if params.role_id > -1:
            user_model.role_id = params.role_id

        db.commit()


def delete_user(id: int) -> None:
    with get_session() as db:
        # TODO: 关联数据删除
        db.query(UserModel).filter_by(id=id).delete()
        db.commit()


def autoreg_from_wechatoauth2(userinfo: dict, session: dict, ip: str = None) -> int:
    '''微信OAuth2授权后, 自动注册或更新用户, 返回用户id'''
    with get_session() as db:
        # 微信返回: 0未知, 1男, 2女
        sexes = [GenderType.UNKNOWN.value,
                 GenderType.MALE.value, GenderType.FEMALE.value]
        if userinfo['sex'] not in sexes:
            gender = GenderType.UNKNOWN.value
        else:
            gender = sexes[userinfo['sex']]

        user = db.query(UserModel).filter(
            UserModel.wechat_openid == userinfo['openid']).first()
        if user is not None:
            user.avatar = userinfo['headimgurl']
            user.nickname = userinfo['nickname']
            user.gender = gender
            user.wechat_refresh_token = session['refresh_token']
            user.wechat_access_token = session['access_token']
            user.wechat_access_token_expired_at = int(
                time.time()) + session['expires_in']
            db.commit()
        else:
            password_salt = secrets.token_urlsafe(32)
            user = UserModel(
                phone=None,
                email=None,
                avatar=userinfo['headimgurl'],
                nickname=userinfo['nickname'],
                password_salt=password_salt,
                password_hash=None,  # 微信自动注册用户暂不设置密码
                role_id=0,
                gender=gender,
                join_from=JoinFromType.FRONTEND_WXOA.value,
                join_ip=ip,
                join_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                wechat_openid=session['openid'],
                wechat_unionid=session.get('unionid', None),
                wechat_refresh_token=session['refresh_token'],
                wechat_access_token=session['access_token'],
                wechat_access_token_expired_at=int(
                    time.time()) + session['expires_in']
            )
            db.add(user)
            db.commit()

        user = db.query(UserModel).filter(UserModel.id == user.id).first()
        return user.to_dict()
