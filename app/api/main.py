#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: main.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

from fastapi import APIRouter

from app.api import routes, frontend, backend


api_router = APIRouter()

# 通用路由
api_router.include_router(routes.auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes.wechat.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes.common.router, prefix="/common", tags=["commons"])

# 前端路由
api_router.include_router(frontend.user.router, prefix="/portal", tags=['portal_user'])

# 后端路由
api_router.include_router(backend.cms.router, prefix="/admin", tags=['admin_cms'])
api_router.include_router(backend.finance.router, prefix="/admin", tags=['admin_finance'])
api_router.include_router(backend.user.router, prefix="/admin", tags=['admin_user'])
api_router.include_router(backend.system_option.router, prefix="/admin", tags=['admin_system_option'])
