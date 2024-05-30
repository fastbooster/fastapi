#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 11:39

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, PositiveInt, validator
from typing import Optional

from app.schemas.schemas import PaginationParams


class BalancType(Enum):
    '''余额类别 正数为收入, 负数为支出/提现'''
    TYPE_RECHARGE = 1  # 充值
    TYPE_RECHARGE_GIFT = 2  # 充值赠送
    TYPE_WITHDRAW_REFUND = 3  # 提现被拒绝时, 资金返回用户余额
    TYPE_PAY_REFUND = 9  # 余额支付退款
    TYPE_ADD = 99  # 后台增加余额
    TYPE_RECHARGE_REFUND = -1  # 充值退款
    TYPE_WITHDRAW = -3  # 提现
    TYPE_PAY = -9  # 余额支付
    TYPE_DEDUCTION = -99  # 后台扣除余额


class PointType(Enum):
    '''积分类别 正数为收入, 负数为支出'''
    TYPE_RECHARGE = 1  # 充值
    TYPE_RECHARGE_GIFT = 2  # 充值赠送
    TYPE_CHECKIN = 3  # 签到获得积分
    TYPE_PULL_NEW = 4  # 拉新获得积分
    TYPE_PULL_NEW_CHECKIN = 5  # 新用户签到, 上级用户获得积分
    TYPE_PAY_REFUND = 9  # 积分支付退款
    TYPE_ADD = 99  # 后台增加积分
    TYPE_RECHARGE_REFUND = -1  # 充值退款
    TYPE_PAY = -9  # 积分支付
    TYPE_DEDUCTION = -99  # 后台扣除积分


class CheckinType(Enum):
    TYPE_CHECKIN = 1  # 签到
    TYPE_COMPLEMENT = 2  # 补签


class PaymentAccountType(Enum):
    TYPE_ALIPAY = 1  # 支付宝
    TYPE_WXPAY = 2  # 微信
    TYPE_BANK = 3  # 银行卡


class SearchQuery(PaginationParams):
    user_id: Optional[int] = 0
    type: Optional[int] = 0


class AdjustForm(BaseModel):
    user_id: PositiveInt
    type: BalancType
    amount: int | float
    related_id: Optional[int] = int(datetime.now().timestamp())
    ip: Optional[str] = None
    hash: Optional[str] = None
    auto_memo: Optional[str] = None
    back_memo: Optional[str] = None

    @validator('amount')
    def validate_amount(cls, value):
        if value == 0:
            raise ValueError('金额不能为0')
        return value

    # type 只支持99和-99
    @validator('type')
    def validate_type(cls, value):
        if value not in [BalancType.TYPE_ADD, BalancType.TYPE_DEDUCTION]:
            raise ValueError('类型错误')
        return value


class PaymentAccountSearchQuery(PaginationParams):
    id: Optional[int] = 0
    user_id: Optional[int] = 0
    type: Optional[int] = 0
    status: Optional[int] = -1
    account: Optional[str] = None


class PaymentAccountFrontendSearchQuery(BaseModel):
    id: Optional[int] = 0
    type: Optional[int] = 0
    status: Optional[int] = -1
    account: Optional[str] = None


class PaymentAccountAddForm(BaseModel):
    type: PaymentAccountType = PaymentAccountType.TYPE_ALIPAY
    account: str
    status: Optional[int] = 1
    user_memo: Optional[str] = None

    @validator('account')
    def validate_account(cls, value):
        if value.find('@') != -1:
            return value
        elif value.isdigit() and len(value) == 11:
            return value
        else:
            raise ValueError('支付宝账号格式错误')

    @validator('type')
    def validate_amount(cls, value):
        if value == PaymentAccountType.TYPE_ALIPAY:
            return value
        else:
            raise ValueError('目前只支持支付宝')


class PaymentAccountEditForm(PaymentAccountAddForm):
    id: int
