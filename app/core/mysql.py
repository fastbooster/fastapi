#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: mysql.py
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
from app.core.log import logger

load_dotenv()

# 连接池耗尽排查
# https://docs.sqlalchemy.org/en/20/errors.html#error-3o7r

# 配置 MySQL 连接参数
pool_size_env = os.getenv("DB_POOL_SIZE")
db_port_env = os.getenv("DB_PORT")
pool_size = int(pool_size_env) if pool_size_env else 5
MYSQL_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(db_port_env) if db_port_env else 3306,
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PWD"),
    'database': os.getenv("DB_NAME"),
    'charset': os.getenv("DB_CHARSET"),
}

# 使用 SQLAlchemy 创建 Engine，并指定连接池作为连接源
engine = create_engine(
    'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format(
        **MYSQL_CONFIG),
    pool_pre_ping=True,  # 在每次获取连接时检查连接是否有效
    pool_recycle=-1,  # 定时自动回收连接，防止有未关闭的连接将连接池耗尽
    pool_timeout=10,  # 连接池超时时间, 此时间内从池子获取不到连接则抛出异常
    pool_size=pool_size,  # 连接池大小
    max_overflow=pool_size * 2,
    # max_overflow=0,  # 不允许 SQLAlchemy 创建额外连接
    # poolclass=db_pool.Pool, # 使用自定义的其他连接池类
)

# 创建 ORM Session 工厂
SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Session = scoped_session(SessionFactory)


def get_url() -> str:
    return 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format(**MYSQL_CONFIG)


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
    session = None
    try:
        session = Session()
        yield session
    except Exception as e:
        logger.error(f"数据库操作发生异常：{e}")
        raise
    finally:
        if session is not None and session.is_active:
            # session.close()
            Session.remove()
