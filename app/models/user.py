#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:12

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, TIMESTAMP
from app.models.base import Base


class RoleModel(Base):
    __tablename__ = 'user_role'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '角色表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(50), nullable=False,
                  comment='角色名称', index=True, unique=True)
    permissions = Column(Text, comment='权限列表')  # json格式
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    def __repr__(self):
        return f"<RoleModel(id={self.id}, name='{self.name}')>"


class PermissionModel(Base):
    __tablename__ = 'user_permission'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '权限表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, server_default='0', comment='上级ID', index=True)
    name = Column(String(50), nullable=False, comment='名称')
    icon = Column(String(50), comment='图标')
    component_name = Column(String(50), comment='路由组件名称')
    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    def __repr__(self):
        return f"<PermissionModel(id={self.id}, name='{self.name}')>"


class UserModel(Base):
    __tablename__ = 'user_account'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '用户表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, server_default='0', comment='所属上级', index=True)
    agent_id = Column(Integer, server_default='0', comment='所属代理')

    phone_code = Column(String(10), server_default='86',
                        comment='手机代码', index=True)
    phone = Column(String(50), comment='手机', index=True, unique=True)
    email = Column(String(50), comment='邮箱', index=True, unique=True)

    nickname = Column(String(50), comment='昵称')
    gender = Column(String(50), comment='性别')
    avatar = Column(String(255), comment='头像')

    promotion_code = Column(String(50), comment='推广码')
    password_salt = Column(String(255), comment='密码盐')
    password_hash = Column(String(255), comment='密码哈希')

    role_id = Column(Integer, server_default='0', comment='角色ID', index=True)
    is_admin = Column(SmallInteger, server_default='0', comment='是否管理员')
    is_robot = Column(SmallInteger, server_default='0', comment='是否机器人')
    status = Column(SmallInteger, server_default='1', comment='状态')

    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')

    wechat_openid = Column(String(50), comment='OpenID', index=True)
    wechat_unionid = Column(String(50), comment='UnionID', index=True)
    wechat_refresh_token = Column(String(255), comment='微信RefreshToken')
    wechat_access_token = Column(String(255), comment='微信AccessToken')
    wechat_access_token_expired_at = Column(
        Integer, comment='微信AccessToken过期时间')

    join_from = Column(SmallInteger, server_default='0', comment='注册来源')
    join_ip = Column(String(50), comment='注册IP')
    join_at = Column(TIMESTAMP, comment='注册时间')

    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    def __repr__(self):
        return f"<UserModel(id={self.id}, nickname='{self.nickname}')>"


class UsermetaModel(Base):
    __tablename__ = 'user_metadata'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '用户元数据'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    meta_key = Column(String(50), nullable=False, comment='键')
    meta_val = Column(Text, comment='值')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_search = Index(None, user_id, meta_key)

    def __repr__(self):
        return f"<UsermetaModel(id={self.id}, user_id='{self.user_id}', meta_key='{self.meta_key}')>"


class LoginlogModel(Base):
    __tablename__ = 'user_loginlog'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '登录日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID', index=True)
    nickname = Column(String(50), comment='昵称')
    ip = Column(String(50), comment='IP地址')
    user_agent = Column(String(500), comment='浏览器信息')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')

    def __repr__(self):
        return f"<LoginlogModel(id={self.id}, nickname='{self.nickname}')>"
