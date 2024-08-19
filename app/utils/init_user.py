#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: init_user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 20:59

import datetime
import hashlib
import os
import secrets

import pymysql
from dotenv import load_dotenv
from loguru import logger

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


def has_user() -> bool:
    try:
        sql = 'select count(1) as "total" from user_account'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return False
            if result['total'] > 0:
                logger.info(f'发现 {result["total"]} 个用户！')
                return True
            return False
    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')


def init_user(params: dict):
    # TODO: 校验手机和邮箱是否已经存在以及各式是否正确
    try:
        sql = '''
        INSERT INTO user_account
        (phone, email, nickname, password_salt, password_hash, role_id, is_admin, join_from, join_ip, join_at)
        VALUES (%s, %s, %s, %s, %s, 1, 1, 2000, '127.0.0.1', %s)
        '''
        with connection.cursor() as cursor:
            val = (params['phone'], params['email'], params['nickname'],
                   params['password_salt'], params['password_hash'],
                   datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            cursor.execute(sql, val)
        connection.commit()
    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')


if __name__ == "__main__":
    password_text = secrets.token_urlsafe(6)
    password_salt = secrets.token_urlsafe(32)
    password_hash = encode_password(password_text, password_salt)
    if has_user():
        logger.info('系统中已存在用户, 跳过初始化, 不过您仍然可以使用以下数据手动添加用户!')
        logger.info(f'password_salt: {password_salt}')
        logger.info(f'password_hash: {password_hash}')
        logger.info(f'明文密码: {password_text}')
        exit(0)

    phone = input('请输入手机号码: ')
    email = input('请输入邮箱地址: ')
    nickname = input('请输入昵称: ')

    init_user({
        'phone': phone,
        'email': email,
        'nickname': nickname,
        'password_salt': password_salt,
        'password_hash': password_hash,
    })

    logger.success(f'初始化管理员成功，明文密码: {password_text}')
    connection.close()
