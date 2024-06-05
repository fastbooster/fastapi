#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/6/4 10:12

import os
import multiprocessing
from wechatpy import WeChatPay
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from app.schemas.config import Settings
from app.core.log import logger


class PaymentManager:
    settings = Settings()
    instances = {}

    def __init__(self):
        manager = multiprocessing.Manager()
        self._lock = manager.Lock()

    def get_instance(self, payment_tool: str, appid: str = None):
        if not appid:
            appid = self._get_default_appid(payment_tool)

        key = f"{payment_tool}_{appid}_{os.getpid()}"
        try:
            self._lock.acquire()
            if key not in self.instances:
                self.instances[key] = self._create_instance(payment_tool, appid)
        finally:
            self._lock.release()
        return self.instances[key]

    def _get_default_appid(self, payment_tool):
        default_config = getattr(self.settings.PAY, payment_tool.upper(), [{}])[0]
        return default_config.appid

    def _create_instance(self, payment_tool, appid):
        config = self._get_payment_config(payment_tool, appid)
        if not config:
            raise ValueError(f"未找到支付配置: {appid}")
        if payment_tool == 'wechat':
            return WeChatPay(
                appid=appid,
                sub_appid=getattr(config, 'miniAppId', None),
                api_key=getattr(config, 'key'),
                mch_id=getattr(config, 'mchId'),
                sub_mch_id=getattr(config, 'subMchId', None),
                mch_cert=getattr(config, 'apiClientCert'),
                mch_key=getattr(config, 'apiClientKey'),
                sandbox=getattr(config, 'sandbox', False),
            )
        elif payment_tool == 'alipay':
            alipay_client_config = AlipayClientConfig(sandbox_debug=getattr(config, 'sandbox', False))
            alipay_client_config.app_id = appid
            alipay_client_config.app_private_key = getattr(config, 'appPrivateKey')
            alipay_client_config.alipay_public_key = getattr(config, 'alipayPublicKey')
            return DefaultAlipayClient(alipay_client_config, logger)
        else:
            raise ValueError(f"不支持当前支付方式: {payment_tool}")

    def _get_payment_config(self, payment_tool, appid):
        configs = getattr(self.settings.PAY, payment_tool.upper(), [])
        for config in configs:
            if payment_tool == 'wechat':
                # 兼容小程序支付, 小程序支付回调返回的appid是小程序的appid, 而不是微信配置项里面的appid
                if config.appid == appid or config.miniAppId == appid or config.mchId == appid:
                    return config
            else:
                if config.appid == appid:
                    return config

        return None


# 创建 PaymentManager 单例
payment_manager = PaymentManager()
