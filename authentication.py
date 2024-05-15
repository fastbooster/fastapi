#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: start.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import hashlib
import hmac
import re
from datetime import datetime, timedelta
from typing import Type

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import UserModel
from utils.mysql import get_db


class BearAuthException(Exception):
    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "HIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


def validate_password(password) -> bool:
    if len(password) < 6:
        return False
    if not re.search("[0-9]", password) or not re.search("[a-zA-Z]", password):
        return False
    return True


def encode_password(input_string) -> str:
    sha_signature = hashlib.sha256(input_string.encode()).hexdigest()
    return sha_signature


def verify_password(plain_password, hashed_password) -> bool:
    pwd_hash = encode_password(plain_password)
    return hmac.compare_digest(hashed_password, pwd_hash)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(data: str) -> str:
    to_encode = {"sub": data}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_payload(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload_sub: str = payload.get("sub")
        if payload_sub is None:
            raise BearAuthException("Token could not be validated")
        return payload_sub
    except JWTError:
        raise BearAuthException("Token could not be validated")


def authenticate_user(db: Session, employee_id: str, password: str) -> Type[UserModel] | bool:
    """调用此方法的接口，拿到 user 对象后会进行更新，所以使用 with_for_update() 锁定行，避免事务竞争"""
    user = db.query(UserModel).with_for_update().filter(UserModel.employee_id == employee_id).first()
    if not user:
        connection = db.connection().engine.raw_connection()
        cursor = connection.cursor()
        cursor.execute(f"select [操作员ID], [操作员工号] from [系统_操作人员表] where [操作员工号] = '{employee_id}'")
        exists_userdata = cursor.fetchone()
        if exists_userdata is not None:
            # 自动添加用户并设置初始密码
            password_hash = encode_password("123456")
            new_user = UserModel(employee_id=employee_id, password_hash=password_hash)
            db.add(new_user)
            db.flush()
            db.commit()

            user = db.query(UserModel).with_for_update().filter(UserModel.employee_id == employee_id).first()
            return user
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Type[UserModel]:
    try:
        employee_id = get_token_payload(token)
    except BearAuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(UserModel).filter(UserModel.employee_id == employee_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def get_current_employee_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        employee_id = get_token_payload(token)
    except BearAuthException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate bearer token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return employee_id


class AuthChecker:
    """
    如果不需要详细的用户信息，使用 get_current_employee_id() 即可不经过查数据库
    或者使用 Redis 解决方案
    """

    # def __call__(self, user: UserModel = Depends(get_current_user)) -> UserModel:
    #     return user

    def __call__(self, employee_id: str = Depends(get_current_employee_id)) -> str:
        return employee_id
