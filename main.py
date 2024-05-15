#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: start.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.main import api_router

load_dotenv()
RUNTIME_MODE = os.getenv("RUNTIME_MODE")

openapi_url = None if RUNTIME_MODE == "PROD" else "/openapi.json"
docs_url = None if RUNTIME_MODE == "PROD" else "/docs"
redoc_url = None if RUNTIME_MODE == "PROD" else "/redoc"

app = FastAPI(openapi_url=openapi_url, docs_url=docs_url, redoc_url=redoc_url)
app.include_router(api_router, prefix="/api/v1")

# https://github.com/tiangolo/fastapi/discussions/10968
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建运行时目录
runtime_path = "./runtime"
if not os.path.exists(runtime_path):
    os.mkdir(runtime_path)

scheduler = BackgroundScheduler()
scheduler.start()


@app.on_event("startup")
def startup_event():
    pass


@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
