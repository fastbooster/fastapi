#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: mysql.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from app.core.log import logger

load_dotenv()

# 开启 SQLAlchemy 调试日志
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

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


def get_url(read_only: bool = False) -> str:
    if read_only:
        MYSQL_CONFIG["host"] = os.getenv("DB_HOST_RO")
    return 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}'.format(**MYSQL_CONFIG)


write_engine = create_engine(
    get_url(read_only=False),
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=-1,
    pool_size=pool_size,
    max_overflow=pool_size * 2,
)
read_engine = create_engine(
    get_url(read_only=True),
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=-1,
    pool_size=pool_size,
    max_overflow=pool_size * 2,
)
WriteSessionFactory = sessionmaker(
    bind=write_engine, autoflush=False, autocommit=False)
WriteSession = scoped_session(WriteSessionFactory)
ReadSessionFactory = sessionmaker(
    bind=read_engine, autoflush=False, autocommit=False)
ReadSession = scoped_session(ReadSessionFactory)


def get_db(read_only: bool = False):
    """
    依赖注入适用，在函数中使用时，需要使用 `db: Session = Depends(get_db)` 声明依赖。
    ```python
    def func(db: Session = Depends(get_db(False))):
        pass
    ```
    """
    db = None
    try:
        db = WriteSession() if not read_only else ReadSession()
        yield db
    except Exception as e:
        logger.error(f"get_db(read_only={read_only}) 数据库操作发生异常：{e}")
        raise
    finally:
        if db is not None and db.is_active:
            if not read_only:
                WriteSession.remove()
            else:
                ReadSession.remove()


@contextmanager
def get_session(read_only: bool = False):
    session = None
    try:
        session = WriteSession() if not read_only else ReadSession()
        yield session
    except Exception as e:
        logger.error(f"get_session(read_only={read_only}) 数据库操作发生异常：{e}")
        raise
    finally:
        if session is not None and session.is_active:
            if not read_only:
                WriteSession.remove()
            else:
                ReadSession.remove()
