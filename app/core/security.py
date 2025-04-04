#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: security.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.constants.constants import REDIS_AUTH_USER_PREFIX, REDIS_AUTH_TTL
from app.core.log import logger
from app.core.mysql import get_session
from app.core.redis import get_redis
from app.models.user import UserModel
from app.schemas.schemas import StatusType


class BearAuthException(Exception):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# PROD多进程模型下，SECRET_KEY 需要使用环境变量来保证密钥统一，否则会导致不同进程间密钥不一致
ALGORITHM = 'HS256'
SECRET_KEY = os.getenv('SECRET_KEY_BASE') or 'fastapi'


def raise_forbidden():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate bearer token',
        headers={'www-authenticate': 'Bearer'}
    )


def validate_password(password) -> bool:
    """检查密码是否符合规范"""
    if len(password) < 6:
        return False
    if not re.search("[0-9]", password) or not re.search("[a-zA-Z]", password):
        return False
    return True


def encode_password(pwd: str, salt: str) -> str:
    """将密码和盐进行加密, 修改此方法需要修改数据库中的密码"""
    sha_signature = hashlib.sha256(
        f'{pwd[::-1]}{salt[::-1]}'.encode()).hexdigest()
    return sha_signature


def verify_password(plain_password: str, salt: str, hashed_password: str) -> bool:
    pwd_hash = encode_password(plain_password, salt)
    return hmac.compare_digest(hashed_password, pwd_hash)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | Any) -> str:
    expire = datetime.now(timezone.utc) + timedelta(seconds=REDIS_AUTH_TTL)
    # 注意: sub 必须强制为字符串，否则会解码失败
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str = Depends(oauth2_scheme)) -> str | Any:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload.get("sub")
    except JWTError as e:
        raise BearAuthException(f'Token could not be validated: {e}')


def authenticate_user_by_password(password: str, phone: str = None, email: str = None) -> dict:
    with get_session(read_only=True) as db:
        if phone is not None:
            user = db.query(UserModel).filter_by(phone=phone).first()
        elif email is not None:
            user = db.query(UserModel).filter_by(email=email).first()
        else:
            raise BearAuthException('手机或邮箱必须填写一个')

        if not user or not verify_password(password, user.password_salt, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="账号或密码错误")

        if user.status == StatusType.DISABLED.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

        user_data = user.__dict__
        user_data.pop('_sa_instance_state', None)

        return user_data


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """根据 token 获取用户ID"""
    try:
        user_id = get_token_payload(token)
        return int(user_id)
    except BearAuthException as e:
        logger.warning(e)
        raise_forbidden()


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """根据 token 获取用户信息"""
    try:
        user_id = get_token_payload(token)
        with get_session(read_only=True) as db:
            user = db.query(UserModel).filter_by(id=user_id).first()
            if not user:
                raise_forbidden()
            user_data = user.__dict__
            user_data.pop('_sa_instance_state', None)
            return user_data
    except BearAuthException as e:
        logger.warning(e)
        raise_forbidden()


def get_current_user_from_cache(token: str = Depends(oauth2_scheme)) -> dict:
    """根据 token 从登录缓存中获取用户信息"""
    try:
        user_id = get_token_payload(token)
        with get_redis() as redis:
            user_data = json.loads(redis.get(f'{REDIS_AUTH_USER_PREFIX}{user_id}'))

        if not user_data:
            logger.warning(f'Could not validate bearer token: {token}')
            raise_forbidden()

        return user_data
    except BearAuthException as e:
        logger.warning(e)
        raise_forbidden()


class AuthChecker:
    """
    ### 是否登录检测

    如果不需要详细的用户信息，使用 get_current_user_id() 即可不经过查数据库
    或者使用 Redis 解决方案
    """

    # 需要用户详细信息时使用
    # def __call__(self, user: dict = Depends(get_current_user)) -> dict:
    #     return user

    # 不需要用户详细信息时使用, 仅检测 token 是否有效，不查数据库
    def __call__(self, user_id: int = Depends(get_current_user_id)) -> None:
        pass


def check_permission(component_name: str):
    """#### 菜单权限检测

    该函数接受 component_name 参数，并返回一个内部函数 permission_checker函数
    permission_checker 函数负责实际的权限检查逻辑，并接受通过 Depends 注入的 user_id，
    这样，component_name 就可以作为一个参数传递给 check_permission，而不是直接传递给 Depends
    TODO: 细化权限粒度，而不是只检查菜单权限
    """

    async def permission_checker(user_data: dict = Depends(get_current_user_from_cache)) -> None:
        if component_name not in user_data['permissions']:
            logger.warning(
                f'用户 (id={user_data["id"]}, nickname={user_data["nickname"]}) 尝试访问未授权的权限组件 {component_name}')
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return permission_checker
