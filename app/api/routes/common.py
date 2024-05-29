#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: common.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 09:51

from loguru import logger
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.constants.constants import RESPONSE_OK
from app.core.security import get_current_user_from_cache, get_current_user_id
from app.services import upload, sms, system_option, city

router = APIRouter()


@router.post('/upload_file', summary='上传文件')
async def upload_file(file: UploadFile = File(...), related_type: str = 'files', related_id: int = 0,
                      user_data: dict = Depends(get_current_user_from_cache)):
    # 调用上传文件方法
    return await upload.upload_file(file, related_type, related_id, user_data)


@router.post('/send_sms', summary='发送短信验证码, 仅用于非登陆下的操作, 比如注册、登录、找回密码等')
async def send_sms(phone: str):
    try:
        await sms.send_sms(phone, 0)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'发送短信验证码失败：{e}')
        raise HTTPException(status_code=500, detail='发送短信验证码失败')
    return RESPONSE_OK


@router.post('/send_sms2', summary='发送短信操作码, 仅用于已登陆下的操作, 比如重置密码')
async def send_sms(phone: str, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        await sms.send_sms(phone, 1)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'发送短信验证码失败：{e}')
        raise HTTPException(status_code=500, detail='发送短信验证码失败')
    return RESPONSE_OK


@router.get('/option/{option_name}', summary='获取系统配置')
async def get_option(option_name: str):
    option = system_option.get_option_by_name(option_name)
    if not option:
        raise HTTPException(status_code=404, detail="系统选项不存在")
    return system_option.safe_whitelist_fields(option.__dict__)


@router.get('/city/{pid}', summary='获取指定上级行政地区的下级行政地区')
async def get_option(pid: int):
    return city.get_city_list(pid)
