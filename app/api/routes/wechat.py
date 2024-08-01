#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/20 11:05

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
from app.services import user as UserService
from app.schemas.user import ChangePwdForm
from app.schemas.auth import WechatOAuth2Form, WechatOAuth2CallbackForm, WechatOAuth2Response, AuthSuccessResponse
from app.core.redis import get_redis
from app.core.mysql import get_session
from app.utils.helper import serialize_datetime

from app.core.wechat import wechat_manager
from app.constants.constants import REDIS_WECHAT, REDIS_AUTH_TTL, REDIS_AUTH_USER_PREFIX
from app.schemas.config import Settings
from app.schemas.schemas import MysqlBoolType

from wechatpy.oauth import WeChatOAuth
from wechatpy.exceptions import WeChatOAuthException

router = APIRouter()


@router.post("/wechat/get_authorize_url", response_model=WechatOAuth2Response, summary="公众号登录第一步：获取微信授权登录地址（可选）")
def wechatOAuth(params: WechatOAuth2Form):
    '''
    注意：授权地址也可以完全在前端拼接完成，不一定从后端获取
    1. (推荐) 前后端分离，如果传入的 ``redirect_uri`` 是一个前端地址，则需要前端 ``POST`` 请求将 ``code`` 和 ``state`` 传到后端完成``注册/登录``
    2. 如果不传入 ``redirect_uri`` 将直接跳转至 ``GET`` ``/wechat/code2user`` 接口，完成``注册/登录``并跳转到前端首页
    '''
    with get_redis() as redis:
        cache_data = redis.hget(REDIS_WECHAT, params.appid)
        if cache_data is None:
            raise HTTPException(
                status_code=400, detail=f'微信媒体平台(appid={params.appid})不存在，请先添加配置')
        wechat_config = json.loads(cache_data)
        if not wechat_config:
            raise HTTPException(
                status_code=400, detail=f'微信媒体平台(appid={params.appid})不存在，请先添加配置')

    settings = Settings()
    redirect_uri = params.redirect_uri
    if redirect_uri is None:
        redirect_uri = f"{settings.ENDPOINT.api}/api/v1/wechat/code2user"

    state = params.state
    if state is None:
        state = params.appid
    else:
        state = f'{params.appid}_{state}'

    fields = {
        'app_id': wechat_config['appid'],
        'secret': wechat_config['appsecret'],
        'redirect_uri': redirect_uri,
        'scope': 'snsapi_userinfo',
        'state': state,
    }

    oauthClient = WeChatOAuth(**fields)
    return WechatOAuth2Response(authorize_url=oauthClient.authorize_url)


@router.get("/wechat/code2user", summary="公众号登录第二步：通过 code 获取用户信息")
def code2user_get(params: WechatOAuth2CallbackForm, request: Request):
    params.ip = request.client.host if request.client else None,
    user = code2user(params)
    raise HTTPException(status_code=400, detail='暂未实现')


@router.post("/wechat/code2user", response_model=AuthSuccessResponse, summary="公众号登录第二步：通过 code 获取用户信息，自动登录（前后端分离, 推荐）")
def code2user_post(params: WechatOAuth2CallbackForm, request: Request):
    params.ip = request.client.host if request.client else None,
    user_data = code2user(params)

    user_id_str = f'{user_data['id']}'
    access_token = create_access_token(subject=user_id_str)

    with get_redis() as redis:
        redis.set(f'{REDIS_AUTH_USER_PREFIX}{user_id_str}',
                  json.dumps(user_data, default=serialize_datetime),
                  ex=REDIS_AUTH_TTL)

    with get_session() as db:
        loginlog = LoginlogModel(
            user_id=user_data['id'],
            nickname=user_data['nickname'],
            ip=request.client.host if request.client else None,
            user_agent=str(request.headers.get('User-Agent')),
        )
        db.add(loginlog)
        db.commit()

    return AuthSuccessResponse(
        access_token=access_token,
        user_data=UserService.safe_whitelist_fields(user_data),
    )


def code2user(params: WechatOAuth2CallbackForm) -> dict:
    '''自动注册/更新用户并返回用户模型的字典数据'''
    appid = params.get_appid()
    with get_redis() as redis:
        cache_data = redis.hget(REDIS_WECHAT, appid)
        if cache_data is None:
            raise HTTPException(
                status_code=400, detail=f'微信媒体平台(appid={appid})不存在')
        wechat_config = json.loads(cache_data)
        if not wechat_config:
            raise HTTPException(
                status_code=400, detail=f'微信媒体平台(appid={appid})不存在')
    fields = {
        'app_id': wechat_config['appid'],
        'secret': wechat_config['appsecret'],
        'redirect_uri': None,
        'state': params.state,
    }
    try:
        oauthClient = WeChatOAuth(**fields)
        access_token = oauthClient.fetch_access_token(params.code)
        user_info = oauthClient.get_user_info()
        return UserService.autoreg_from_wechatoauth2(
            user_info, access_token, ip=params.ip)
    except WeChatOAuthException as e:
        raise HTTPException(status_code=400, detail=e.errmsg)
