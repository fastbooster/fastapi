#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: wechat.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/25 16:23

from sqlalchemy import text, Column, Integer, String, TIMESTAMP

from app.models.base import Base, BaseMixin


class WechatModel(Base, BaseMixin):
    __tablename__ = 'wechat_media_platform'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '微信媒体平台'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(String(50), nullable=False, comment='账号类型')
    appid = Column(String(50), comment='AppID', index=True, unique=True)
    appname = Column(String(50), comment='AppName')
    appsecret = Column(String(50), comment='AppSecret')
    token = Column(String(50), comment='Token')
    aeskey = Column(String(43), comment='AesKey')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<WechatModel(id={self.id}, appid='{self.appid}')>"
