#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: start.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from authentication import (AuthChecker, authenticate_user, create_access_token,
                            validate_password,
                            encode_password,
                            verify_password,
                            get_current_user)
from models import UserModel
from forms import ChangePwdForm
from utils.mysql import get_db

router = APIRouter()


@router.post("/token", summary="用户登录")
def authorize(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(
        db=db, employee_id=form.username, password=form.password)
    if not user:
        raise HTTPException(status_code=401, detail="工号或密码错误")
    try:
        access_token = create_access_token(data=user.employee_id)
        chg_pwd = True if user.password_hash == encode_password(
            "123456") or form.password == "123456" else False

        # user.access_token = access_token
        # user.last_login_at = int(time.time())
        # user.last_login_ip = request.client.host
        # user.user_agent = request.headers.get("user-agent")
        # db.commit()

        return {
            "token_type": "bearer",
            "username": form.username,
            "access_token": access_token,
            "change_password": chg_pwd,
        }
    except Exception as e:
        print(f"登录失败: {e}")
        db.close()
        raise HTTPException(
            status_code=500, detail=f"未知错误，请联系技术支持: {e}")


@router.post("/logout", summary="用户登出")
def logout():
    pass


@router.post("/change_password", summary="修改密码", dependencies=[Depends(AuthChecker())])
def change_password(form: ChangePwdForm, user: UserModel = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not validate_password(form.new_pwd):
        raise HTTPException(status_code=400, detail="新密码过于简单，请重新输入")
    if not verify_password(form.old_pwd, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")
    user.password_hash = encode_password(form.new_pwd)
    db.commit()
    db.close()
    return {"status": "OK"}
