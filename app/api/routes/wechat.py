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
from app.core.redis import get_redis
from app.core.mysql import get_session
from app.utils.helper import serialize_datetime

from app.constants.constants import RESPONSE_OK, REDIS_AUTH_TTL, REDIS_AUTH_USER_PREFIX

from wechatpy import WeChatClient

router = APIRouter()

@router.post("/wechat", summary="微信登录")
def wechat():
    pass
