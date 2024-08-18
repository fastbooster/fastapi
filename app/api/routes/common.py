#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: common.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 09:51

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.core.log import logger
from app.core.security import get_current_user_from_cache
from app.schemas.schemas import ResponseSuccess
from app.schemas.system_option import SystemOptionPublicItem
from app.services import upload, sms, system_option, city, ad

router = APIRouter()


@router.post('/upload_file', summary='上传文件')
async def upload_file(file: UploadFile = File(...), related_type: str = 'files', related_id: int = 0,
                      user_data: dict = Depends(get_current_user_from_cache)):
    return await upload.upload_file(file, related_type, related_id, user_data)


@router.post('/send_sms', response_model=ResponseSuccess,
             summary='发送短信验证码, 用于非登陆的情况下, 比如注册、登录、找回密码等')
async def send_sms(phone: str):
    try:
        await sms.send_sms(phone, 0)
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'发送短信验证码失败：{e}')
        raise HTTPException(status_code=500, detail='发送短信验证码失败')


@router.post('/send_sms2', response_model=ResponseSuccess, summary='发送短信操作码, 用于已登陆的情况下, 比如重置密码')
async def send_sms(phone: str, user_data: dict = Depends(get_current_user_from_cache)):
    try:
        await sms.send_sms(phone, 1)
        return ResponseSuccess()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f'{e}')
    except Exception as e:
        logger.error(f'发送短信验证码失败：{e}')
        raise HTTPException(status_code=500, detail='发送短信验证码失败')


@router.get('/options/{option_name}', response_model=SystemOptionPublicItem, summary='获取系统配置')
async def get_option(option_name: str):
    option = system_option.get_option_by_name(option_name)
    if option is None or option.public != 1:
        raise HTTPException(status_code=404, detail="系统选项不存在")
    return option


@router.get('/city/{pid}', summary='获取指定上级行政地区的下级行政地区')
async def get_option(pid: int):
    return city.get_city_list(pid)


@router.get('/ad/{space_id}', summary='获取指定广告位的广告列表')
def ad_list(space_id: int):
    items = ad.get_ad_list_from_cache(space_id)
    return [ad.safe_whitelist_fields(item) for item in items]
