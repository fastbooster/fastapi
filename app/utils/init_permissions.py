#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: init_permissions.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 09:39

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


def init_permissions():
    menus = [
        {
            'name': '仪表盘',
            'component_name': 'Dashboard',
            'children': [
                {
                    'name': '欢迎登录',
                    'component_name': 'DashboardOverview',
                }
            ]
        },
        {
            'name': '用户管理',
            'component_name': 'User',
            'children': [
                {
                    'name': '用户列表',
                    'component_name': 'UserList',
                },
                {
                    'name': '管理员列表',
                    'component_name': 'AdminList',
                }
            ]
        },
        {
            'name': '内容管理',
            'component_name': 'CMS',
            'children': [
                {
                    'name': '文章分类',
                    'component_name': 'PostCategoryList',
                },
                {
                    'name': '文章列表',
                    'component_name': 'PostList',
                },
                {
                    'name': '广告位列表',
                    'component_name': 'AdSpaceList',
                }
            ]
        },
        {
            'name': '充值提现',
            'component_name': 'Finance',
            'children': [
                {
                    'name': '充值设置',
                    'component_name': 'RechargeSettings',
                },
                {
                    'name': '积分充值记录',
                    'component_name': 'PoitRecharges',
                },
                {
                    'name': '余额充值记录',
                    'component_name': 'BalanceRecharges',
                },
                {
                    'name': '余额提现记录',
                    'component_name': 'Withdrawal',
                },
            ]
        },
        {
            'name': '权限管理',
            'component_name': 'Permission',
            'children': [
                {
                    'name': '角色列表',
                    'component_name': 'RoleList',
                },
                {
                    'name': '权限列表',
                    'component_name': 'PermissionList',
                }
            ]
        },
        {
            'name': '系统设置',
            'component_name': 'Settings',
            'children': [
                {
                    'name': '系统选项',
                    'component_name': 'SystemOption',
                },
            ]
        },
    ]

    connection = pymysql.connect(**MYSQL_CONFIG)

    try:
        i = 0
        pid = 0
        sql = 'INSERT INTO user_permission (pid, name, component_name, asc_sort_order) VALUES (%s, %s, %s, %s)'
        with connection.cursor() as cursor:
            cursor.execute('truncate table user_permission')
            logger.success(f'清空权限表成功！')

            for menu in menus:
                asc_sort_order = (i + 1) * 1000
                val = (0, menu['name'], menu['component_name'], asc_sort_order)
                cursor.execute(sql, val)
                asc_sort_order += 1
                i += 1
                pid = i
                logger.info(f'{menu["name"]}')

                j = 0
                for submenu in menu['children']:
                    asc_sort_order_sub = asc_sort_order + j
                    val = (
                        pid, submenu['name'], submenu['component_name'], asc_sort_order_sub)
                    cursor.execute(sql, val)
                    j += 1
                    logger.info(f'\t{submenu["name"]}')
                i += j

        connection.commit()

        logger.success('初始化权限成功！')

    except pymysql.MySQLError as e:
        logger.error(f'Database error: {e}')

    finally:
        connection.close()


if __name__ == "__main__":
    init_permissions()
