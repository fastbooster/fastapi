#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment_settings.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/07/09 00:07

from sqlalchemy import text, Text, Index, Column, Integer, String, TIMESTAMP
from app.models.base import Base, BaseMixin


class PaymentChannelModel(Base, BaseMixin):
    __tablename__ = 'payment_channel'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '支付渠道'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')

    # 用于缓存键, eg: alipay, wechatpay, unionpay, channelN
    key = Column(String(50), comment='键名')

    # 用于前端显示, eg: 支付宝, 微信支付, 银联支付, 支付通道N
    name = Column(String(50), comment='名称')
    
    icon = Column(String(255), comment='图标')

    # 系统内置的支付渠道不可删除
    locked = Column(String(10), server_default='no', comment='锁定: yes/no')

    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    status = Column(String(10), nullable=False,
                    server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_key = Index('idx_key', key, unique=True)
    idx_sort = Index('idx_sort', asc_sort_order)

    def __repr__(self):
        return f"<PaymentChannelModel(id={self.id}, key='{self.key}')>"


class PaymentConfigModel(Base, BaseMixin):
    __tablename__ = 'payment_config'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '支付配置'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    channel_id = Column(Integer, nullable=False, comment='支付渠道ID')

    # 用于前端显示, eg: 支付宝, 微信支付, 银联支付, 支付通道N
    name = Column(String(50), comment='名称')
    appname = Column(String(50), comment='支付平台APP名称')
    appid = Column(String(50), nullable=False, comment='支付平台APPID')
    mchid = Column(String(50), comment='支付平台商户ID')
    miniappid = Column(String(50), comment='小程序APPID')  # 微信专用

    app_public_cert = Column(Text(), comment='应用公钥')
    app_private_key = Column(Text(), comment='应用私钥')

    # 微信支付，其他聚合平台会有密钥，可设置到此字段保存
    app_secret_key = Column(Text(), comment='应用密钥')

    # 支付宝专用
    platform_public_cert = Column(Text(), comment='平台公钥')

    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    status = Column(String(10), nullable=False,
                    server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_sort = Index('idx_sort', asc_sort_order)

    def __repr__(self):
        return f"<PaymentConfigModel(id={self.id}, user_id='{self.name}')>"
