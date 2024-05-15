#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: start.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os
import pymysql
from contextlib import contextmanager 
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dbutils.pooled_db import PooledDB
from dotenv import load_dotenv

load_dotenv()


# 配置 MySQL 连接参数
pool_size = int(os.getenv("DB_POOL"))
MYSQL_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASS"),
    'database': os.getenv("DB_NAME"),
}

# 创建 PyMySQL 连接池
db_pool = PooledDB(
    creator=pymysql,  # 使用 PyMySQL 作为连接器
    maxconnections=5,  # 最大连接数，根据实际情况调整
    mincached=2,  # 初始连接数
    maxcached=5,  # 最大空闲连接数
    blocking=True,  # 当连接耗尽时是否阻塞等待
    maxusage=None,  # 单个连接的最大复用次数（None 表示无限制）
    setsession=[],  # 连接建立后执行的 SQL 命令列表（如设置字符集）
    **MYSQL_CONFIG,
)

# 使用 SQLAlchemy 创建 Engine，并指定连接池作为连接源
engine = create_engine(
    'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'.format(
        **MYSQL_CONFIG),
    pool_pre_ping=True,  # 在每次获取连接时检查连接是否有效
    pool_recycle=3600,  # 每小时回收一次连接
    pool_size=pool_size,  # 不再指定 PoolSize，因为已使用外部连接池
    # max_overflow=0,  # 不允许 SQLAlchemy 创建额外连接
    # poolclass=db_pool.Pool,
)

# 创建 ORM Session 工厂
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """
    上下文管理器，用于获取数据库会话对象，并在上下文结束时自动关闭会话。
    """
    db = None
    try:
        db = Session()
        yield db  # 将会话对象提供给上下文使用
    finally:
        if db is not None:
            db.close()


@contextmanager
def get_session():
    """
    上下文管理器，用于获取数据库会话对象，并在上下文结束时自动关闭会话。
    """
    db = None
    try:
        db = Session()
        yield db  # 将会话对象提供给上下文使用
    finally:
        if db is not None:
            db.close()
