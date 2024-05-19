#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: constants.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/18 21:46

# 操作成功返回的数据，当不需要返回数据时，统一直接返回该数据
RESPONSE_OK = {'status': 'OK'}

# 登录有效期
REDIS_AUTH_TTL = 86400

# user:1
REDIS_AUTH_USER_PREFIX = 'logged_user:'
