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
api_router.include_router(frontend.finance.router, prefix="/frontend", tags=['frontend_finance'])
api_router.include_router(frontend.user.router, prefix="/frontend", tags=['frontend_user'])
api_router.include_router(frontend.balance_recharge.router, prefix="/frontend", tags=['frontend_balance_recharge'])

# 后端路由
api_router.include_router(backend.adspace.router, prefix="/backend", tags=['backend_adspace'])
api_router.include_router(backend.banner.router, prefix="/backend", tags=['backend_banner'])
api_router.include_router(backend.post.router, prefix="/backend", tags=['backend_post'])
api_router.include_router(backend.post_category.router, prefix="/backend", tags=['backend_post_category'])
api_router.include_router(backend.finance.router, prefix="/backend", tags=['backend_finance'])
api_router.include_router(backend.role.router, prefix="/backend", tags=['backend_role'])
api_router.include_router(backend.permissions.router, prefix="/backend", tags=['backend_permission'])
api_router.include_router(backend.user.router, prefix="/backend", tags=['backend_user'])
api_router.include_router(backend.system_option.router, prefix="/backend", tags=['backend_system_option'])
api_router.include_router(backend.payment_channel.router, prefix="/backend", tags=['backend_payment_channel'])
api_router.include_router(backend.payment_config.router, prefix="/backend", tags=['backend_payment_config'])
api_router.include_router(backend.payment_settings.router, prefix="/backend", tags=['backend_payment_settings'])
api_router.include_router(backend.balance_recharge.router, prefix="/backend", tags=['backend_balance_recharge'])
api_router.include_router(backend.wechat.router, prefix="/backend", tags=['backend_wechat'])
api_router.include_router(backend.cache.router, prefix="/backend", tags=['backend_cache'])
