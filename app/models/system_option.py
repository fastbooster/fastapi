#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: system_option.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/19 13:09

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, TIMESTAMP
from app.models.base import Base


class SystemOptionModel(Base):
    __tablename__ = 'system_option'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '系统选项'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    option_name = Column(String(32), comment='选项名称')
    option_value = Column(Text, comment='选项值')
    richtext = Column(SmallInteger, server_default='0', comment='是否富文本')
    position = Column(SmallInteger, server_default='0', comment='位置')
    autoload = Column(SmallInteger, server_default='0', comment='自动加载')
    lock = Column(SmallInteger, server_default='0', comment='禁止删除')
    memo = Column(String(255), comment='备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_option_name = Index('idx_option_name', option_name)
    idx_memo = Index('idx_memo', memo)
    idx_position_autoload = Index('idx_position_autoload', position, autoload)

    def __repr__(self):
        return f"<SystemOptionModel(id={self.id}, option_name='{self.option_name}')>"
