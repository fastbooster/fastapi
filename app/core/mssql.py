#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: mssql.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

driver = os.getenv("DB_DRIVER")
server = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
name = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
pwd = os.getenv("DB_PWD")
pool_size = os.getenv("DB_POOL_SIZE")
pool_size = int(pool_size) if pool_size else 5

connection_string = f"mssql+pyodbc://{user}:{
    pwd}@{server}/{name}?driver={driver}"
# engine = create_engine(connection_string)

# 降低 pool_recycle 时间，防止连接数耗尽
engine = create_engine(
    connection_string, pool_size=pool_size, pool_recycle=60)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
