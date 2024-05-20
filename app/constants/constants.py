#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: constants.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/18 21:46

import os

# 应用根目录
ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 应用文件存储目录
UPLOAD_PATH = ROOT_PATH + '/public'

# 操作成功返回的数据，当不需要返回数据时，统一直接返回该数据
RESPONSE_OK = {'status': 'OK'}

# 登录有效期
REDIS_AUTH_TTL = 86400

# 默认邮箱后缀，当用户注册时，如果邮箱为空，则自动使用 user_id@DEFAULT_EMAIL_SUFFIX
DEFAULT_EMAIL_SUFFIX = '@fastapi.com'

# user:1
REDIS_AUTH_USER_PREFIX = 'logged_user:'

# [hash] 系统参数配置
REDIS_SYSTEM_OPTIONS_AUTOLOAD = 'system_options_autoload'
