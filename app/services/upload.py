#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: upload.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 10:37

import os
import random
import re
import time

from fastapi import UploadFile
from app.constants.constants import UPLOAD_PATH
from app.core.mysql import get_session
from app.models.cms import MediaModel


async def upload_file(file: UploadFile, related_type: str, related_id: int, user_data: dict, file_exts: str = None):
    # 文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    # 允许上传文件后缀
    item_exts = file_exts.split("|") if file_exts else ['.jpeg', '.jpg', '.png', '.gif', '.xls', '.xlsx', '.doc', '.docx', '.pdf', '.mp4', '.mp3']
    if file_ext not in item_exts:
        raise ValueError('文件格式不正确')

    related_type = related_type.lower()
    # /^[a-z0-9_]{1,32}$/i
    if not re.match(r'^[a-z0-9_]{1,32}$', related_type):
        raise ValueError('文件类型不正确')

    # 定义文件名，时分秒随机数用户id
    file_name = f"{time.strftime('%H%M%S')}_{random.randint(0, 9999):04d}_{user_data['id']}"
    # 重写合成文件名
    file_name = os.path.join(file_name + file_ext)

    # 保存文件
    save_path = UPLOAD_PATH + '/' + related_type + '/' + time.strftime('%Y%m%d')
    # 创建存放目录
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 拼接文件路径
    data = await file.read()
    path = save_path + '/' + file_name
    # 写入文件
    with open(path, 'wb') as f:
        f.write(data)
        f.close()

    # 文件地址
    oss_assets_url = str(os.getenv('OSS_ASSETS_URL'))
    oss_assets_url = oss_assets_url.rstrip('/')
    if not re.match(r'^https?://', oss_assets_url):
        oss_assets_url = 'https://' + oss_assets_url
    oss_url = oss_assets_url + path.replace(UPLOAD_PATH, '')

    # 保存到数据库
    with get_session() as db:
        option_model = MediaModel(
            file_name=file.filename,
            file_type=file.content_type,
            file_size=os.path.getsize(path),
            file_path=path.replace(UPLOAD_PATH + '/', ''),
            oss_url=oss_url,
            op_user_id=user_data['id'],
            op_user_name=user_data['nickname'],
            related_type=related_type,
            related_id=related_id,
        )

        db.add(option_model)
        db.commit()

    # 返回结果
    result = {
        'type': related_type,
        'url': oss_url,
    }
    # 返回结果
    return result
