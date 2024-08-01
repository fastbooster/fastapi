#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: auth.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/26 01:23


import time
from typing import Optional
from pydantic import BaseModel, Field, AnyHttpUrl, validator
from app.schemas.schemas import MysqlBoolType
from app.constants.constants import REDIS_AUTH_TTL


class WechatOAuth2Form(BaseModel):
    '''微信公众号OAuth2认证登录表单'''
    appid: str = Field(
        pattern=r"^wx[a-zA-Z0-9]{1,62}$", description="微信公众号APPID")
    scope: Optional[str] = Field(
        'snsapi_base', description="scope参数，snsapi_base：不弹出授权页面，直接跳转，只能获取用户openid；snsapi_userinfo：弹出授权页面，可通过 openid 拿到昵称、头像信息")
    state: Optional[str] = Field(
        None, description="state参数，用于保持请求和回调的状态，本系统会自动加上 appid 作为前缀")
    redirect_uri: Optional[str] = Field(
        None, description="用户在微信侧授权完成后的跳转地址，会携带 code 和 state 参数，用于后续完成用户信息的获取")


class WechatOAuth2Response(BaseModel):
    authorize_url: AnyHttpUrl = Field(description="微信授权地址，用于跳转到微信授权页面")


class WechatOAuth2CallbackForm(BaseModel):
    '''微信公众号OAuth2认证回调表单，参数来至微信侧返回的 ``code`` 和 ``state`` 参数'''
    code: str = Field(description="微信OAuth2授权后返回的code参数")
    state: str = Field(description="state参数，用于保持请求和回调的状态")
    ip: Optional[str] = Field(None, description="用户IP地址, 无需传入，即使传入也不会被采纳")

    def get_appid(self) -> str:
        return self.state.split('_', 1)[0]


class AuthSuccessResponse(BaseModel):
    token_type: str = 'bearer'
    access_token: str = Field(description='授权码')
    user_data: dict = Field(description='用户数据')
    expires_at: int = Field(
        int(time.time()) + REDIS_AUTH_TTL, description='过期时间')
