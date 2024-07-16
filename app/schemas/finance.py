#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: finance.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/21 11:39

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, PositiveInt, validator, Field, HttpUrl
from typing import List, Optional

from app.schemas.schemas import ClientType, PaginationParams


class BalanceType(Enum):
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


class PaymentStatuType(Enum):
    PAYMENT_STATUS_CREATED = 0  # 创建成功, 仅此状态可以进行支付
    PAYMENT_STATUS_SUCCESS = 1  # 支付成功
    PAYMENT_STATUS_FAIL = 2  # 支付失败
    PAYMENT_STATUS_CLOSE = 3  # 已关闭
    PAYMENT_STATUS_REFUND_APPLY = 4  # 退款中
    PAYMENT_STATUS_REFUND_APART = 5  # 部分退款
    PAYMENT_STATUS_REFUND_SUCCESS = 6  # 已退款
    PAYMENT_STATUS_REFUND_FAIL = 7  # 退款失败


class PaymentToolType(Enum):
    PAYMENT_TOOL_WECHAT = 'wechatpay'  # 原生微信
    PAYMENT_TOOL_ALIPAY = 'alipay'  # 原生支付宝
    PAYMENT_TOOL_EXCHANGE = 'exchange'  # 兑换券
    PAYMENT_TOOL_BALANCE = 'balance'  # 余额支付


class SearchQuery(PaginationParams):
    user_id: Optional[int] = 0
    type: Optional[int] = 0


class AdjustForm(BaseModel):
    user_id: PositiveInt
    type: BalanceType
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
        if value not in [BalanceType.TYPE_ADD, BalanceType.TYPE_DEDUCTION]:
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


class PointRechargeSettingItem(BaseModel):
    exchange_rate: Optional[float] = Field(
        None, description="兑换比例：1元人民币=多少积分, 此项为自定义充值积分专用")
    amount: Optional[int] = Field(None, gt=0, description="用户获得的积分")
    gift_amount: Optional[int] = Field(0, ge=0, description="用户获得的赠送积分")
    original_price: Optional[float] = Field(None, gt=0, description="原价")
    price: Optional[float] = Field(None, gt=0, description="实际支付价格")
    desc: Optional[str] = Field(None, description="描述")
    status: int = Field(1, ge=0, le=1, description="状态：0-禁用，1-启用")

    @validator('price')
    def validate_price(cls, value, values):
        # 这里values只会包含当前字段之前的其他字段, 要注意字段的顺序
        original_price = values.get('original_price')
        if original_price is not None and value > original_price:
            raise ValueError('价格不能大于原价')
        return value


class BalanceRechargeSettingItem(PointRechargeSettingItem):
    exchange_rate: Optional[float] = Field(
        None, description="兑换比例：1元人民币=多少余额, 此项为自定义充值金额专用")
    amount: Optional[int | float] = Field(None, gt=0, description="用户获得的充值金额")
    gift_amount: Optional[int | float] = Field(
        None, ge=0, description="用户获得的赠送金额")


class PointRechargeSettingListResponse(BaseModel):
    items: List[PointRechargeSettingItem]


class BalanceRechargeSettingListResponse(BaseModel):
    items: List[BalanceRechargeSettingItem]


class RechargeForm(BaseModel):
    '''充值表单，余额和积分充值共用此表单'''
    sku_id: int = Field(ge=0, description="充值套餐id，从0开始, 来至充值设置")
    price: Optional[float] = Field(None, gt=0, description="自定义充值金额，此时根据 exchange_rate 计算出实际到账金额或积分")


class PayForm(BaseModel):
    '''支付表单，所有支付业务在生成订单后，需构造此表单向相应接口提交以唤起支付'''
    client: ClientType = Field(ClientType.PC_BROWSER.value, description="发起支付的客户端类型, 返回结果将挂在此字段下")
    channel: str = Field(description="支付渠道Key，详见支付设置/支付渠道，例如：alipay, wechatpay, balance")
    appid: str = Field(description="支付配置AppID，详见支付设置/支付配置，例如：2014040501377004")
    trade_no: str = Field(description="订单号")
    openid: Optional[str] = Field(None, description="微信支付时，支付用户的openid")
    return_url: Optional[HttpUrl] = Field(None, description="同步返回地址")
    notify_url: Optional[HttpUrl] = Field(None, description="异步通知地址")


class ScanpayForm(BaseModel):
    '''扫码支付表单，PC端页面显示二维码，手机扫码支付，扫码落地页构建此表单向相应接口提交以唤起支付'''
    trade_no: str
    client: Optional[ClientType] = Field(ClientType.WECHAT_BROWSER.value, description="发起支付的客户端类型")
    openid: Optional[str] = None

    @validator('client')
    def validate_client(cls, value):
        if value not in ['alipay', 'wechat']:
            raise ValueError('客户端类型错误')
        return value
