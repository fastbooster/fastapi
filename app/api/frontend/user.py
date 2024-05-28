#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 20:13

from fastapi import APIRouter, HTTPException, Depends, Request

from app.core.security import get_current_user_from_cache
from app.services import user as UserService
from app.services import finance as FinanceService
from app.core.log import logger
from app.constants.constants import RESPONSE_OK

router = APIRouter()


@router.get("/user/me", summary="我的详情")
def my_detail(user_data: dict = Depends(get_current_user_from_cache)):
    return UserService.safe_whitelist_fields(user_data)


@router.post("/user/checkin", summary="用户签到")
def checkin(request: Request, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        ip = request.client.host if request.client else None
        user_agent = str(request.headers.get('User-Agent'))
        FinanceService.checkin(user_data['id'], ip, user_agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'签到失败：{e}')
        raise HTTPException(status_code=500, detail='签到失败')
    return RESPONSE_OK
