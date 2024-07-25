#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: constants.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/18 21:46

import os
from wechatpy.pay.utils import dict_to_xml

# 应用根目录
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 应用文件存储目录
UPLOAD_PATH = ROOT_PATH + '/public'

# 应用文件存储目录
RUNTIME_PATH = ROOT_PATH + '/runtime'

# 结果返回给微信服务器时的成功返回数据
RESPONSE_WECHAT_SUCCESS = dict_to_xml({'return_code': 'SUCCESS', 'return_msg': 'OK'})

# 结果返回给微信服务器时的失败返回数据
RESPONSE_WECHAT_FAIL = dict_to_xml({'return_code': 'FAIL', 'return_msg': 'FAIL'})

# 结果返回给支付宝服务器时的成功返回数据
RESPONSE_ALIPAY_SUCCESS = 'success'

# 结果返回给支付宝服务器时的失败返回数据
RESPONSE_ALIPAY_FAIL = 'failure'

# 登录有效期
REDIS_AUTH_TTL = 86400

# 默认邮箱后缀，当用户注册时，如果邮箱为空，则自动使用 user_id@DEFAULT_EMAIL_SUFFIX
DEFAULT_EMAIL_SUFFIX = '@fastapi.com'

# user:1
REDIS_AUTH_USER_PREFIX = 'logged_user:'

# [hash] 系统参数配置
REDIS_SYSTEM_OPTIONS_AUTOLOAD = 'system_options_autoload'

# [hash] 支付渠道
REDIS_PAYMENT_CHANNEL = 'payment_channel'

# [hash] 支付配置
REDIS_PAYMENT_CONFIG = 'payment_config'

# [hash] 微信媒体平台
REDIS_WECHAT = 'wechat'

# 接手机号码, 同一个号码30分钟内只能发送10次, 只统计发送成功的次数
REDIS_SMS_COUNT = 'sms:count:'

# 30分钟内允许发送验证码的次数
REDIS_SMS_LIMIT = 10

# 验证码, 接类型+手机号, eg: 0130xxxxxxxx (前面的0表示验证码类型为0), 存验证码
REDIS_SMS_CODE_PREFIX = 'sms:code:'

# [hash] 储存文章分类的全部值
REDIS_POST_CATEGORY = 'post:category'

# 接广告位ID, 存广告资源
REDIS_AD_PREFIX = 'ad:'
