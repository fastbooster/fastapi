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
    TYPE_WITHDRAW_ROLLBACK = 2  # 提现被拒绝时, 资金返回用户余额
    TYPE_ADD = 99  # 后台增加余额
    TYPE_WITHDRAW = -1  # 提现
    TYPE_BALANCE_PAY = -2  # 余额支付
    TYPE_DEDUCTION = -99  # 后台扣除余额


class PointType(Enum):
    '''积分类别 正数为收入, 负数为支出'''
    TYPE_RECHARGE = 1  # 充值
    TYPE_CHECKIN = 2  # 签到获得积分
    TYPE_PULL_NEW = 3  # 拉新获得积分
    TYPE_PULL_NEW_CHECKIN = 4  # 新用户签到, 上级用户获得积分
    TYPE_REFUND = 5  # 退款加积分
    TYPE_ADD = 99  # 后台增加积分
    TYPE_EXCHANGE = -1  # 积分兑换
    TYPE_RECHARGE_REFUND = -2  # 充值退款
    TYPE_DEDUCTION = -99  # 后台扣除积分


class CheckinType(Enum):
    TYPE_CHECKIN = 1  # 签到
    TYPE_COMPLEMENT = 2  # 补签


class SearchQuery(PaginationParams):
    user_id: int


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
