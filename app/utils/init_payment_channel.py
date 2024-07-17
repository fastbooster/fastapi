#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: init_payment_channel.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 09:55

import os
import pymysql
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


def has_item() -> bool:
    try:
        sql = 'select count(1) as "total" from payment_channel'
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                return False
            if result['total'] > 0:
                logger.info(f'发现 {result["total"]} 个支付渠道！')
                return True
            return False
    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')


def init_items():
    items = [
        {
            'id': 1,
            'key': 'balance',
            'name': '余额支付',
            'icon': '',
            'locked': 'yes',
            'status': 'enabled',
            'children': [
                {
                    'appid': '10000',
                    'name': '余额钱包',
                    'locked': 'yes',
                    'status': 'enabled',
                },
                {
                    'appid': '20000',
                    'name': '积分钱包',
                    'locked': 'yes',
                    'status': 'enabled',
                },
            ],
        },
        {
            'id': 2,
            'key': 'alipay',
            'name': '支付宝',
            'icon': '',
            'locked': 'yes',
            'status': 'enabled',
        },
        {
            'id': 3,
            'key': 'wechatpay',
            'name': '微信支付',
            'icon': '',
            'locked': 'yes',
            'status': 'enabled',
        },
    ]

    try:
        sql_chanel = 'INSERT INTO payment_channel (`key`, `name`, `icon`, `locked`, `asc_sort_order`, `status`) VALUES (%s, %s, %s, %s, %s, %s)'
        sql_config = 'INSERT INTO payment_config (`channel_id`, `channel_key`, `name`, `appname`, `appid`, `locked`, `asc_sort_order`, `status`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        with connection.cursor() as cursor:
            cursor.execute('truncate table payment_channel')
            logger.success(f'清空支付渠道表成功！')

            cursor.execute('truncate table payment_config')
            logger.success(f'清空支付配置表成功！')

            asc_sort_order = 1
            for item in items:
                val = (item['key'], item['name'], item['icon'],
                       item['locked'], asc_sort_order, item['status'])
                cursor.execute(sql_chanel, val)
                asc_sort_order += 1
                logger.info(f'{item["name"]}')

                asc_sort_order_cofig = 1
                if 'children' in item:
                    for child in item['children']:
                        val = (item['id'], item['key'], child['name'], child['name'], child['appid'],
                               item['locked'], asc_sort_order_cofig, child['status'])
                        cursor.execute(sql_config, val)
                        asc_sort_order_cofig += 1
                        logger.info(f'\t{child["name"]}')

        connection.commit()

        logger.success('初始化支付渠道成功！')

    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')

    finally:
        connection.close()


if __name__ == "__main__":
    if has_item():
        logger.info('系统中已存在支付渠道, 跳过初始化!')
        exit(0)

    init_items()
