#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: auth.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import json

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import (AuthChecker, authenticate_user_by_password, create_access_token,
                               validate_password,
                               encode_password,
                               verify_password,
                               get_current_user)
from app.models.user import UserModel
from app.models.user import RoleModel
from app.models.user import LoginlogModel
from app.schemas.user import ChangePwdForm
from app.core.redis import get_redis
from app.core.mysql import get_session
from app.utils.helper import serialize_datetime

from app.constants.constants import REDIS_AUTH_TTL, REDIS_AUTH_USER_PREFIX

router = APIRouter()


@router.post("/token", summary="用户登录")
def authorize(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    user_data = authenticate_user_by_password(
        password=form.password, phone=form.username, email=form.username)
    if not user_data:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    subject = f'{user_data['id']}'
    access_token = create_access_token(subject=subject)

    # 获取用户权限列表
    if user_data['role_id']:
        with get_session() as db:
            # 目前只支持单用户单角色模式
            user_role = (db.query(RoleModel)
                         .filter_by(id=user_data['role_id'])
                         .first())
            if user_role:
                user_data['permissions'] = user_role.permissions

    with get_redis() as redis:
        redis.set(f'{REDIS_AUTH_USER_PREFIX}{user_data['id']}',
                  json.dumps(user_data, default=serialize_datetime),
                  ex=REDIS_AUTH_TTL)

    with get_session() as db:
        loginlog = LoginlogModel(
            user_id=user_data['id'],
            nickname=user_data['nickname'],
            ipaddr=request.client.host,
            user_agent=str(request.headers.get('User-Agent')),
        )
        db.add(loginlog)
        db.commit()

    return {
        'token_type': 'bearer',
        'access_token': access_token,
        'user_data': {
            'id': user_data['id'],
            'nickname': user_data['nickname'],
            'gender': user_data['gender'],
            'avatar': user_data['avatar'],
        },
    }


@router.post("/logout", summary="用户登出")
def logout():
    pass


@router.post("/change_password", summary="修改密码", dependencies=[Depends(AuthChecker())])
def change_password(form: ChangePwdForm, user_data: dict = Depends(get_current_user)):
    if not validate_password(form.new_pwd):
        raise HTTPException(status_code=400, detail="新密码过于简单，请重新输入")
    if not verify_password(form.old_pwd, user_data['password_salt'], user_data['password_hash']):
        raise HTTPException(status_code=400, detail="旧密码错误")

    with get_session() as db:
        user = db.query(UserModel).filter_by(id=user_data['id']).first()
        user.password_hash = encode_password(form.new_pwd, user.password_salt)
        db.commit()

    return {"status": "OK"}
