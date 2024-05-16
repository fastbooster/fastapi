#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:12

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, TIMESTAMP
from app.models.base import Base


class RoleModel(Base):
    __tablename__ = 'role'
    __table_args__ = {'comment': '角色表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(50), nullable=False, comment='角色名称')
    permissions = Column(Text, comment='权限列表')  # json格式
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class PermissionModel(Base):
    __tablename__ = 'permission'
    __table_args__ = {'comment': '权限表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, server_default='0', comment='上级ID')
    name = Column(String(50), nullable=False, comment='名称')
    icon = Column(String(50), comment='图标')
    component_name = Column(String(50), comment='路由组件名称')
    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class UserModel(Base):
    __tablename__ = 'user'
    __table_args__ = {'comment': '用户表'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, server_default='0', comment='所属上级')
    agent_id = Column(Integer, server_default='0', comment='所属代理')

    phone_code = Column(String(10), server_default='86', comment='手机代码')
    phone = Column(String(50), comment='手机')
    email = Column(String(50), comment='邮箱')

    nickname = Column(String(50), comment='昵称')
    gender = Column(String(50), comment='性别')
    avatar = Column(String(255), comment='头像')

    promotion_code = Column(String(50), comment='推广码')
    password_salt = Column(String(255), comment='密码盐')
    password_hash = Column(String(255), comment='密码哈希')

    role_id = Column(Integer, server_default='0', comment='角色ID')
    is_admin = Column(SmallInteger, server_default='0', comment='是否管理员')
    is_robot = Column(SmallInteger, server_default='0', comment='是否机器人')

    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')

    wechat_openid = Column(String(50), comment='OpenID')
    wechat_unionid = Column(String(50), comment='UnionID')
    wechat_refresh_token = Column(String(255), comment='微信RefreshToken')
    wechat_access_token = Column(String(255), comment='微信AccessToken')
    wechat_access_token_expired_at = Column(
        Integer, comment='微信AccessToken过期时间')

    join_ip = Column(Integer, comment='注册IP')
    join_at = Column(TIMESTAMP, comment='注册时间')

    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_pid = Index('idx_pid', pid)
    idx_phone = Index('idx_phone', phone)
    idx_email = Index('idx_email', email)
    idx_role = Index('idx_role', role_id)
    idx_wechat_openid = Index('idx_wechat_openid', wechat_openid)
    idx_wechat_unionid = Index('idx_wechat_unionid', wechat_unionid)

    def __repr__(self):
        return f"<UserModel(id={self.id}, nickname='{self.nickname}')>"


class LoginlogModel(Base):
    __tablename__ = 'loginlog'
    __table_args__ = {'comment': '登录日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    nickname = Column(String(50), comment='昵称')
    ipaddr = Column(String(50), comment='IP地址')
    user_agent = Column(String(500), comment='浏览器信息')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')

    def __repr__(self):
        return f"<LoginlogModel(id={self.id}, nickname='{self.nickname}')>"
