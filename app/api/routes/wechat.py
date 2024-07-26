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
from app.schemas.auth import WechatOAuth2Form, WechatOAuth2Response
from app.core.redis import get_redis
from app.core.mysql import get_session
from app.utils.helper import serialize_datetime

from app.core.wechat import wechat_manager
from app.constants.constants import REDIS_WECHAT
from app.schemas.config import Settings

from wechatpy.oauth import WeChatOAuth

router = APIRouter()


@router.post("/wechat/get_authorize_url", response_model=WechatOAuth2Response, summary="公众号登录第一步：获取微信授权登录地址（可选）")
def wechatOAuth(params: WechatOAuth2Form):
    '''
    注意：授权地址也可以完全在前端拼接完成，不一定从后端获取
    1. (推荐) 前后端分离，如果传入的 ``redirect_uri`` 是一个前端地址，则需要前端 ``POST`` 请求将 ``code`` 和 ``state`` 传到后端完成``注册/登录``
    2. 如果不传入 ``redirect_uri`` 将直接跳转至 ``GET`` ``/wechat/code2user`` 接口，完成``注册/登录``并跳转到前端首页
    '''
    with get_redis() as redis:
        wechat_config = json.loads(redis.hget(REDIS_WECHAT, params.appid))
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
def code2user_get():
    pass


@router.post("/wechat/code2user", summary="公众号登录第二步：通过 code 获取用户信息（前后端分离）")
def code2user_post():
    pass
