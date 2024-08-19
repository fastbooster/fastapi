#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 11:45

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, DECIMAL, TIMESTAMP

from app.models.base import Base, BaseMixin


class BalanceModel(Base, BaseMixin):
    __tablename__ = 'user_balance'
    __table_args__ = (
        Index(None, 'user_id', 'type'),
        Index(None, 'user_id', 'created_at'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '余额日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(SmallInteger, nullable=False, comment='动账类型')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    # related_id 与 type 字段一起可确认关联模型，单独看此字段没有意义
    related_id = Column(Integer, server_default='0', index=True, comment='关联ID')
    amount = Column(DECIMAL(10, 4), nullable=False, comment='动账金额')
    balance = Column(DECIMAL(10, 4), nullable=False, comment='当前余额')
    ip = Column(String(50), comment='IP')
    hash = Column(String(32), comment='校验码')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<BalanceModel(id={self.id}, user_id={self.user_id}, balance={self.balance})>"


class BalanceGiftModel(Base, BaseMixin):
    __tablename__ = 'user_balance_gift'
    __table_args__ = (
        Index(None, 'user_id', 'type'),
        Index(None, 'user_id', 'created_at'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '赠送余额日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(SmallInteger, nullable=False, comment='动账类型')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    # related_id 与 type 字段一起可确认关联模型，单独看此字段没有意义
    related_id = Column(Integer, server_default='0', index=True, comment='关联ID')
    amount = Column(DECIMAL(10, 4), nullable=False, comment='动账金额')
    balance = Column(DECIMAL(10, 4), nullable=False, comment='当前余额')
    ip = Column(String(50), comment='IP')
    hash = Column(String(32), comment='校验码')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<BalanceGiftModel(id={self.id}, user_id={self.user_id}, balance={self.balance})>"


class PointModel(Base, BaseMixin):
    __tablename__ = 'user_point'
    __table_args__ = (
        Index(None, 'user_id', 'type'),
        Index(None, 'user_id', 'created_at'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '积分日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    type = Column(SmallInteger, nullable=False, comment='动账类型')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    # related_id 与 type 字段一起可确认关联模型，单独看此字段没有意义
    related_id = Column(Integer, server_default='0', index=True, comment='关联ID')
    amount = Column(Integer, nullable=False, comment='动账点数')
    balance = Column(Integer, nullable=False, comment='当前余额')
    ip = Column(String(50), comment='IP')
    hash = Column(String(32), comment='校验码')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<PointModel(id={self.id}, user_id={self.user_id}, balance={self.balance})>"


class PaymentAccountModel(Base, BaseMixin):
    __tablename__ = 'user_payment_account'
    __table_args__ = (
        Index(None, 'user_id', 'type', 'status'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '用户支付账号'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    type = Column(String(50), server_default='alipay', comment='类型')
    account = Column(String(50), nullable=False, index=True, comment='账号')
    bank_name = Column(String(50), comment='银行名称')
    bank_outlets = Column(String(255), comment='开户行')
    bank_userphone = Column(String(50), comment='银行预留手机号')
    total_withdraw = Column(DECIMAL(10, 4), comment='累计提现')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    auto_memo = Column(String(255), comment='自动备注')
    user_memo = Column(String(255), comment='用户备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<PaymentAccountModel(id={self.id}, user_id={self.user_id} account='{self.account}')>"


class WithdrawModel(Base, BaseMixin):
    __tablename__ = 'user_withdraw'
    __table_args__ = (
        Index(None, 'user_id', 'payment_status'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '提现日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    account_id = Column(Integer, nullable=False, index=True, comment='提现账号ID')
    trade_no = Column(String(32), nullable=False, comment='交易号')
    amount = Column(DECIMAL(10, 4), nullable=False, comment='提现金额')
    actual_amount = Column(DECIMAL(10, 4), nullable=False, comment='实际到账')
    handling_fee = Column(DECIMAL(10, 4), nullable=False, comment='手续费')
    balance = Column(DECIMAL(10, 4), nullable=False, comment='申请时余额')
    payment_status = Column(SmallInteger, server_default='0', comment='状态')
    payment_channel = Column(String(50), comment='支付渠道')
    payment_appid = Column(String(50), comment='支付APPID')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    audit_status = Column(SmallInteger, server_default='0', index=True, comment='审核状态')
    audit_user_id = Column(Integer, server_default='0', index=True, comment='审核人员ID')
    audit_user_name = Column(String(100), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')
    user_ip = Column(String(50), comment='用户申请时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<WithdrawModel(id={self.id}, user_id={self.user_id}, amount={self.amount})>"


class ChenckinModel(Base, BaseMixin):
    __tablename__ = 'user_checkin'
    __table_args__ = (
        Index(None, 'user_id', 'type'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '签到日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    type = Column(SmallInteger, server_default='1', comment='类型 1:签到 2:补签')
    total_days = Column(Integer, server_default='0', comment='累计签到天数')
    keep_days = Column(Integer, server_default='1', comment='连续签到天数')
    points = Column(Integer, server_default='0', comment='获得积分')
    related_type = Column(String(50), index=True, comment='关联类型')
    related_id = Column(Integer, server_default='0', comment='关联ID')
    ip = Column(String(50), comment='IP地址')
    user_agent = Column(String(500), comment='浏览器信息')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    def __repr__(self):
        return f"<ChenckinModel(id={self.id}, user_id={self.user_id})>"


class BalanceRechargeModel(Base, BaseMixin):
    __tablename__ = 'user_balance_recharge'
    __table_args__ = (
        Index(None, 'user_id', 'payment_status'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '余额充值日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID', index=True)
    trade_no = Column(String(32), nullable=False, unique=True, index=True, comment='交易号')

    amount = Column(DECIMAL(10, 4), nullable=False, comment='充值数量')
    price = Column(DECIMAL(10, 4), nullable=False, comment='支付金额')
    gift_amount = Column(DECIMAL(10, 4), server_default='0', comment='赠送数量')
    refund_amount = Column(DECIMAL(10, 4), server_default='0', comment='退款数量')
    refund_gift_amount = Column(DECIMAL(10, 4), server_default='0', comment='退款赠送数量')

    # 支付状态：0 创建成功/未支付（只有此种状态才能继续执行支付）1 支付成功, 2 支付失败, 3 交易关闭，4 退款中, 5 部分退款, 6 已退全款
    payment_status = Column(SmallInteger, server_default='0', index=True, comment='状态')
    payment_channel = Column(String(50), index=True, comment='支付渠道')
    payment_appid = Column(String(50), comment='支付APPID')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    refund_response = Column(Text, comment='退款结果')

    # 退款审核
    audit_user_id = Column(Integer, server_default='0', index=True, comment='审核人员ID')
    audit_user_name = Column(String(100), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')

    user_ip = Column(String(50), comment='用户充值时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<BalanceRechargeModel(id={self.id}, user_id='{self.user_id}')>"


class PointRechargeModel(Base, BaseMixin):
    __tablename__ = 'user_point_recharge'
    __table_args__ = (
        Index(None, 'user_id', 'payment_status'),
        {
            'mysql_charset': 'utf8mb4',
            'mysql_collate': 'utf8mb4_unicode_ci',
            'mysql_engine': 'InnoDB',
            'mariadb_engine': 'InnoDB',
            'comment': '积分充值日志'
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID', index=True)
    trade_no = Column(String(32), nullable=False, unique=True, index=True, comment='交易号')

    amount = Column(DECIMAL(10, 4), nullable=False, comment='充值金额')
    points = Column(Integer, nullable=False, comment='充值数量')
    gift_points = Column(Integer, server_default='0', comment='赠送数量')
    refund_amount = Column(DECIMAL(10, 4), server_default='0', comment='退款金额')
    refund_points = Column(Integer, server_default='0', comment='退款数量')
    refund_gift_points = Column(Integer, server_default='0', comment='退款赠送数量')

    # 支付状态：0 创建成功/未支付（只有此种状态才能继续执行支付）1 支付成功, 2 支付失败, 3 交易关闭，4 退款中, 5 部分退款, 6 已退全款
    payment_status = Column(SmallInteger, server_default='0', index=True, comment='状态')
    payment_channel = Column(String(50), index=True, comment='支付渠道')
    payment_appid = Column(String(50), comment='支付APPID')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    refund_response = Column(Text, comment='退款结果')

    # 退款审核
    audit_user_id = Column(Integer, server_default='0', index=True, comment='审核人员ID')
    audit_user_name = Column(String(50), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')

    user_ip = Column(String(50), comment='用户充值时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<PointRechargeModel(id={self.id}, user_id={self.user_id}, amount={self.amount})>"
