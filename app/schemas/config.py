#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: config.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/6/3 11:22

import yaml
from pydantic import BaseModel, root_validator
from typing import List
from app.constants.constants import ROOT_PATH, RUNTIME_PATH


class OfficialAccount(BaseModel):
    frontendUrl: str
    callbackUrl: str
    appId: str
    appSecret: str
    token: str
    aesKey: str


class WeChatSettings(BaseModel):
    REFRESH_TOKEN: bool
    PUSH_TOKEN: bool
    PUSH_LIST: List[str]
    OFFICIALACCOUNT: OfficialAccount


class Endpoint(BaseModel):
    sp: str
    pay: str
    api: str
    mp: str
    portal: str
    console: str


class BalancePaymentAccount(BaseModel):
    appname: str
    appid: str
    name: str


class WeChatPaymentAccount(BaseModel):
    sandbox: bool
    appid: str
    appname: str
    name: str
    miniAppId: str
    mchId: str
    key: str
    refundUrl: str
    notifyUrl: str
    apiClientCert: str
    apiClientKey: str


class AlipayPaymentAccount(BaseModel):
    sandbox: bool
    appid: str
    appname: str
    name: str
    alipayRootCert: str
    alipayCertPublicKey: str
    appCertPublicKey: str
    appPrivateKey: str
    alipayPublicKey: str
    returnUrl: str
    notifyUrl: str


class PaymentConfig(BaseModel):
    BALANCE: List[BalancePaymentAccount] = []
    WECHAT: List[WeChatPaymentAccount] = []
    ALIPAY: List[AlipayPaymentAccount] = []


class Settings(BaseModel):
    WECHAT: WeChatSettings
    ENDPOINT: Endpoint
    PAY: PaymentConfig

    @root_validator(pre=True)
    def load_config(cls, values):
        config_file = ROOT_PATH + "/config.yaml"  # 配置文件路径
        with open(config_file) as f:
            config_data = yaml.safe_load(f)

        # 批量替换 {certs_path}占位符 为 RUNTIME_PATH/certs
        config_data = cls._replace_path_placeholder(config_data, "{certs_path}", RUNTIME_PATH + "/certs")

        values.update(config_data)
        return values

    @classmethod
    def _replace_path_placeholder(cls, data, from_str, to_str):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    data[key] = value.replace(from_str, to_str)
                elif isinstance(value, (list, dict)):
                    cls._replace_path_placeholder(value, from_str, to_str)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                cls._replace_path_placeholder(item, from_str, to_str)
        return data
