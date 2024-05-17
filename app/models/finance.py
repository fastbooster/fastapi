#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 11:45

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, DECIMAL, TIMESTAMP
from app.models.base import Base


class BalanceModel(Base):
    __tablename__ = 'balance'
    __table_args__ = {'comment': '余额日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(SmallInteger, nullable=False, comment='动账类型')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    # related_id 与 type 字段一起可确认关联模型，单独看此字段没有意义
    related_id = Column(Integer, server_default='0', comment='关联ID')
    amount = Column(DECIMAL(10, 4), nullable=False, comment='动账金额')
    balance = Column(DECIMAL(10, 4), nullable=False, comment='当前余额')
    ip = Column(String(50), comment='IP')
    hash = Column(String(32), comment='校验码')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_type = Index('idx_user_id_type', user_id, type)

    def __repr__(self):
        return f"<BalanceModel(id={self.id}, user_id='{self.user_id}')>"


class PointModel(Base):
    __tablename__ = 'point'
    __table_args__ = {'comment': '积分日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(SmallInteger, nullable=False, comment='动账类型')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    # related_id 与 type 字段一起可确认关联模型，单独看此字段没有意义
    related_id = Column(Integer, server_default='0', comment='关联ID')
    amount = Column(Integer, nullable=False, comment='动账点数')
    balance = Column(Integer, nullable=False, comment='当前余额')
    ip = Column(String(50), comment='IP')
    hash = Column(String(32), comment='校验码')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_type = Index('idx_user_id_type', user_id, type)

    def __repr__(self):
        return f"<PointModel(id={self.id}, user_id='{self.user_id}')>"
