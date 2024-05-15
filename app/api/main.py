#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: main.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

from fastapi import APIRouter

from app.api.routes import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["登录鉴权"])
