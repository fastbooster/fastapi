#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: common.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 09:51

from fastapi import APIRouter, Depends, UploadFile, File

from app.core.security import get_current_user_from_cache
from app.services import upload

router = APIRouter()

@router.post('/upload_file', summary='上传文件')
async def upload_file(file: UploadFile = File(...), related_type: str = 'files', related_id: int = 0, user_data: dict = Depends(get_current_user_from_cache)):
    # 调用上传文件方法
    return await upload.uploadFile(file, related_type, related_id, user_data)
