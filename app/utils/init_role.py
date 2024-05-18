#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: init_role.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/18 20:27

import os
import secrets
import hashlib
import pymysql
import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# 配置 MySQL 连接参数
MYSQL_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT")),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PWD"),
    'database': os.getenv("DB_NAME"),
    'charset': os.getenv("DB_CHARSET"),
    'cursorclass': pymysql.cursors.DictCursor
}

connection = pymysql.connect(**MYSQL_CONFIG)


def encode_password(pwd: str, salt: str) -> str:
    sha_signature = hashlib.sha256(
        f'{pwd[::-1]}{salt[::-1]}'.encode()).hexdigest()
    return sha_signature


def has_role() -> bool:
    try:
        sql = 'select count(1) as "total" from user_role'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return False
            if result['total'] > 0:
                logger.info(f'发现 {result["total"]} 个角色！')
                return True
            return False
    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')


def init_role():
    try:
        with connection.cursor() as cursor:
            sql = 'select component_name from user_permission where component_name is not null order by asc_sort_order asc'
            cursor.execute(sql)
            result = cursor.fetchall()
            if not result:
                logger.warning('请先初始化权限')
                return

            components = [row['component_name'] for row in result]
            sql = 'insert into user_role (name, permissions) values (%s, %s)'
            val = ("超级管理员", ','.join(components))
            cursor.execute(sql, val)
        connection.commit()
        logger.success(f'初始化权限成功！')
    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')


if __name__ == "__main__":
    password_text = secrets.token_urlsafe(6)
    password_salt = secrets.token_urlsafe(32)
    password_hash = encode_password(password_text, password_salt)
    if has_role():
        logger.info('系统中已存在角色, 初始化终止!')
        exit(0)

    init_role()

    connection.close()
