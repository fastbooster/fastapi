#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 22:12

from sqlalchemy import Column, Integer, String, Date, DECIMAL, PrimaryKeyConstraint, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "tz_report_user"

    employee_id = Column(String(50), primary_key=True, comment="工号")
    password_hash = Column(String(64), comment="密码")
    access_token = Column(String(64), unique=True, comment="密钥")
    last_login_at = Column(Integer, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    user_agent = Column(String(1000), comment="用户代理信息")
