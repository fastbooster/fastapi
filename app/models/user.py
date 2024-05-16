#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:12

from sqlalchemy import Column, Integer, String, Date, DECIMAL, PrimaryKeyConstraint, SmallInteger
from app.models.base import Base


class UserModel(Base):
    __tablename__ = 'user'
    __table_args__ = {'comment': '用户表'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, default=0, comment='所属上级ID')
    agent_id = Column(Integer, default=0, comment='所属代理ID')

    phone_code = Column(String(10), default='86', comment='手机代码')
    phone = Column(String(50), comment='手机')
    email = Column(String(50), comment='邮箱')

    nickname = Column(String(50), comment='昵称')
    gender = Column(String(50), comment='性别')
    avatar = Column(String(255), comment='头像')
    
    password_salt = Column(String(255), comment='密码盐')
    password_hash = Column(String(255), comment='密码哈希')
    
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    
    wechat_openid = Column(String(50), comment='OpenID')
    wechat_unionid = Column(String(50), comment='UnionID')
    promotion_code = Column(String(50), comment='推广码')
    
    role_id = Column(Integer(), default=0, comment='角色ID')
    is_admin = Column(Integer(), default=0, comment='角色ID')

    created_at = Column(Integer, default=0, server_default='CURRENT_TIMESTAMP', comment='创建时间')
    updated_at = Column(Integer, default=0, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP', comment='更新时间')
    
