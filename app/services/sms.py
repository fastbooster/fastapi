#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: sms.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/20 13:16

import json
import os
import re
import random

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from app.constants.constants import REDIS_SMS_COUNT, REDIS_SMS_LIMIT, REDIS_SMS_CODE_PREFIX
from app.core.redis import get_redis
from app.core.security import encode_password, verify_password


async def send_sms(phone: str, type: int) -> bool:
    # type类型, 0登录验证码, 1操作验证码
    if type not in [0, 1]:
        raise ValueError('type类型不正确')

    # 用正则验证手机号
    match = re.match(r'^1\d{10}$', phone)
    if len(phone) != 11:
        raise ValueError('手机号码长度必须为 11 位')
    elif match is None:
        raise ValueError('手机号码格式不正确')

    # 检查30分钟内已发送成功的验证码次数
    with get_redis() as redis:
        count = redis.get(REDIS_SMS_COUNT + phone)
        count = int(count) if count is not None else 0
        if count >= REDIS_SMS_LIMIT:
            raise ValueError('频繁发送, 请稍后重试')

    access_key_id = str(os.getenv('SMS_ACCESS_KEY_ID'))
    access_key_secret = str(os.getenv('SMS_ACCESS_KEY_SECRET'))
    region_id = str(os.getenv('SMS_REGION_ID', 'cn-hangzhou'))
    sign_name = str(os.getenv('SMS_SIGN_NAME'))
    template_code = str(os.getenv('SMS_TEMPLATE_CODE'))
    code = random.randint(100000, 999999)

    client = AcsClient(access_key_id, access_key_secret, region_id)

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', sign_name)
    request.add_query_param('TemplateCode', template_code)
    request.add_query_param('TemplateParam', json.dumps({'code': code}))

    response = client.do_action_with_exception(request)
    response = json.loads(response)
    # 验证响应是否成功 解析响应是否包含Code 并且 Code=OK 缓存验证码
    if response.get('Code') == 'OK':
        with get_redis() as redis:
            # 缓存验证码 180秒
            redis.set(REDIS_SMS_CODE_PREFIX + type + phone, encode_password(str(code), str(code)), 180)
            # 缓存发送次数
            count += 1
            redis.set(REDIS_SMS_COUNT + phone, count, 1800)

        return True
    else:
        msg = response.get('Message') if response.get('Message') else '未知错误'
        raise ValueError(msg)


def check_sms(phone: str = '', code: int = 0, type: int = 0) -> bool:
    # type类型, 0登录验证码, 1操作验证码
    if type not in [0, 1] or len(phone) != 11 or code < 100000 or code > 999999:
        return False

    with get_redis() as redis:
        hashcode = redis.get(REDIS_SMS_CODE_PREFIX + type + phone)
        if verify_password(str(code), str(code), hashcode):
            return True

    return False
