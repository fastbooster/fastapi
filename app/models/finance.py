#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 11:45

from sqlalchemy import text, Text, Index, Column, Integer, SmallInteger, String, DECIMAL, TIMESTAMP
from app.models.base import Base


class BalanceModel(Base):
    __tablename__ = 'user_balance'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '余额日志'}

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
    idx_type_related_id = Index('idx_type_related_id', type, related_id)
    idx_user_id_created_at = Index('idx_user_id_created_at', user_id, created_at)

    def __repr__(self):
        return f"<BalanceModel(id={self.id}, user_id='{self.user_id}')>"


class BalanceGiftModel(Base):
    __tablename__ = 'user_balance_gif'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '赠送余额日志'}

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
    idx_type_related_id = Index('idx_type_related_id', type, related_id)
    idx_user_id_created_at = Index('idx_user_id_created_at', user_id, created_at)

    def __repr__(self):
        return f"<BalanceGiftModel(id={self.id}, user_id='{self.user_id}')>"


class PointModel(Base):
    __tablename__ = 'user_point'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '积分日志'}

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
    idx_type_related_id = Index('idx_type_related_id', type, related_id)
    idx_user_id_created_at = Index('idx_user_id_created_at', user_id, created_at)

    def __repr__(self):
        return f"<PointModel(id={self.id}, user_id='{self.user_id}')>"


class PaymentAccountModel(Base):
    __tablename__ = 'user_payment_account'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '用户支付账号'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    type = Column(SmallInteger, server_default='1', comment='类型')  # 类型 1:支付宝, 2:微信, 3:银行卡
    account = Column(String(255), nullable=False, comment='账号')
    bank_name = Column(String(255), comment='银行名称')
    bank_outlets = Column(String(255), comment='开户行')
    bank_userphone = Column(String(255), comment='银行预留手机号')
    total_withdraw = Column(DECIMAL(10, 2), comment='累计提现')
    status = Column(SmallInteger, server_default='1', comment='状态')
    auto_memo = Column(String(255), comment='自动备注')
    user_memo = Column(String(255), comment='用户备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_type_status = Index('idx_user_id_type_status', user_id, type, status)
    idx_type_account = Index('idx_type_account', type, account)

    def __repr__(self):
        return f"<PaymentAccountModel(id={self.id}, user_id='{self.user_id}')>"


class WithdrawModel(Base):
    __tablename__ = 'user_withdraw'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '提现日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    account_id = Column(Integer, nullable=False, comment='提现账号ID')
    trade_no = Column(String(32), nullable=False, comment='交易号')
    amount = Column(DECIMAL(10, 2), nullable=False, comment='提现金额')
    actual_amount = Column(DECIMAL(10, 2), nullable=False, comment='实际到账')
    handling_fee = Column(DECIMAL(10, 2), nullable=False, comment='手续费')
    balance = Column(DECIMAL(10, 2), nullable=False, comment='申请时余额')
    payment_status = Column(SmallInteger, server_default='0', comment='状态')
    payment_tool = Column(String(50), comment='支付方式')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    audit_status = Column(SmallInteger, server_default='0', comment='审核状态')
    audit_user_id = Column(Integer, server_default='0', comment='审核人员ID')
    audit_user_name = Column(String(100), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')
    user_ip = Column(String(50), comment='用户申请时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_payment_status = Index('idx_user_id_payment_status', user_id, payment_status)
    idx_account_id = Index('idx_account_id', account_id)
    idx_audit_user_id = Index('idx_audit_user_id', audit_user_id)
    idx_audit_status = Index('idx_audit_status', audit_status)
    idx_created_at = Index('idx_created_at', created_at)

    def __repr__(self):
        return f"<WithdrawModel(id={self.id}, user_id='{self.user_id}')>"


class ChenckinModel(Base):
    __tablename__ = 'user_checkin'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '签到日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    type = Column(SmallInteger, server_default='1', comment='类型')  # 类型 1:签到, 2:补签
    total_days = Column(Integer, server_default='0', comment='累计签到天数')
    keep_days = Column(Integer, server_default='1', comment='连续签到天数')
    points = Column(Integer, server_default='0', comment='获得积分')
    related_type = Column(String(100), comment='关联类型')
    related_id = Column(Integer, server_default='0', comment='关联ID')
    ip = Column(String(50), comment='IP地址')
    user_agent = Column(String(500), comment='浏览器信息')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')

    idx_user_id_type = Index('idx_user_id_type', user_id, type)
    idx_related = Index('idx_related', related_type, related_id)

    def __repr__(self):
        return f"<ChenckinModel(id={self.id}, user_id='{self.user_id}')>"


class BalanceRechargeModel(Base):
    __tablename__ = 'user_balance_recharge'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '余额充值日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    trade_no = Column(String(32), nullable=False, comment='交易号')

    amount = Column(DECIMAL(10, 2), nullable=False, comment='充值数量')
    price = Column(DECIMAL(10, 2), nullable=False, comment='支付金额')
    gift_amount = Column(DECIMAL(10, 2), server_default='0', comment='赠送数量')
    refund_amount = Column(DECIMAL(10, 2), server_default='0', comment='退款数量')
    refund_gift_amount = Column(DECIMAL(10, 2), server_default='0', comment='退款赠送数量')

    # 支付状态：0 创建成功/未支付（只有此种状态才能继续执行支付）1 支付成功, 2 支付失败, 3 交易关闭，4 退款中, 5 部分退款, 6 已退全款
    payment_status = Column(SmallInteger, server_default='0', comment='状态')
    payment_tool = Column(String(50), comment='支付方式')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    refund_response = Column(Text, comment='退款结果')

    # 退款审核
    audit_user_id = Column(Integer, server_default='0', comment='审核人员ID')
    audit_user_name = Column(String(100), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')

    user_ip = Column(String(50), comment='用户充值时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_payment_status = Index('idx_user_id_payment_status', user_id, payment_status)
    idx_user_id = Index('idx_user_id', user_id)
    idx_payment_status = Index('idx_payment_status', payment_status)
    idx_trade_no = Index('idx_trade_no', trade_no, unique=True)
    idx_payment_tool = Index('idx_payment_tool', payment_tool)
    idx_audit_user_id = Index('idx_audit_user_id', audit_user_id)
    idx_created_at = Index('idx_created_at', created_at)

    def __repr__(self):
        return f"<BalanceRechargeModel(id={self.id}, user_id='{self.user_id}')>"


class PointRechargeModel(Base):
    __tablename__ = 'user_point_recharge'
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mariadb_engine': 'InnoDB', 'comment': '积分充值日志'}

    mysql_charset = 'utf8mb4'
    mysql_collate = 'utf8mb4_unicode_ci'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    user_id = Column(Integer, nullable=False, comment='用户ID')
    trade_no = Column(String(32), nullable=False, comment='交易号')

    amount = Column(DECIMAL(10, 2), nullable=False, comment='充值金额')
    points = Column(Integer, nullable=False, comment='充值数量')
    gift_points = Column(Integer, server_default='0', comment='赠送数量')
    refund_amount = Column(DECIMAL(10, 2), server_default='0', comment='退款金额')
    refund_points = Column(Integer, server_default='0', comment='退款数量')
    refund_gift_points = Column(Integer, server_default='0', comment='退款赠送数量')

    # 支付状态：0 创建成功/未支付（只有此种状态才能继续执行支付）1 支付成功, 2 支付失败, 3 交易关闭，4 退款中, 5 部分退款, 6 已退全款
    payment_status = Column(SmallInteger, server_default='0', comment='状态')
    payment_tool = Column(String(50), comment='支付方式')
    payment_time = Column(TIMESTAMP, comment='支付时间')
    payment_response = Column(Text, comment='支付结果')
    refund_response = Column(Text, comment='退款结果')

    # 退款审核
    audit_user_id = Column(Integer, server_default='0', comment='审核人员ID')
    audit_user_name = Column(String(100), comment='审核人员姓名')
    audit_reply = Column(String(255), comment='审核回复')
    audit_time = Column(TIMESTAMP, comment='审核时间')
    audit_ip = Column(String(50), comment='审核人员IP地址')

    user_ip = Column(String(50), comment='用户充值时的IP地址')
    auto_memo = Column(String(255), comment='自动备注')
    back_memo = Column(String(255), comment='后台备注')
    created_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

    idx_user_id_payment_status = Index('idx_user_id_payment_status', user_id, payment_status)
    idx_user_id = Index('idx_user_id', user_id)
    idx_payment_status = Index('idx_payment_status', payment_status)
    idx_trade_no = Index('idx_trade_no', trade_no, unique=True)
    idx_payment_tool = Index('idx_payment_tool', payment_tool)
    idx_audit_user_id = Index('idx_audit_user_id', audit_user_id)
    idx_created_at = Index('idx_created_at', created_at)

    def __repr__(self):
        return f"<PointRechargeModel(id={self.id}, user_id='{self.user_id}')>"
