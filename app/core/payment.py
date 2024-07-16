#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: payment.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/6/4 10:12

import os
import json
import multiprocessing
from wechatpy import WeChatPay
from app.schemas.config import Settings
from alipay import AliPay, DCAliPay

from app.core.redis import get_redis

from app.constants.constants import REDIS_PAYMENT_CONFIG, REDIS_SYSTEM_OPTIONS_AUTOLOAD


class PaymentManager:
    settings = Settings()
    instances = {}

    def __init__(self):
        manager = multiprocessing.Manager()
        self._lock = manager.Lock()

    def get_instance(self, channel_key: str, appid: str = None):
        '''TODO: 按支付渠道返回对应的支付实例，方便类型提示'''
        if not appid:
            appid = self._get_default_appid(channel_key)

        key = f"{channel_key}_{appid}_{os.getpid()}"
        try:
            self._lock.acquire()
            if key not in self.instances:
                self.instances[key] = self._create_instance(channel_key, appid)
        finally:
            self._lock.release()
        return self.instances[key]

    def _get_default_appid(self, channel_key: str):
        default_config = getattr(
            self.settings.PAY, channel_key.upper(), [{}])[0]
        return default_config.appid

    def _create_instance(self, channel_key: str, appid: str):
        # TOOD: 兼容从配置文件获取支付配置
        # config = self._get_payment_config(channel_key, appid)
        config = self._get_payment_config_from_cache(appid)
        # print(config)

        if not config:
            raise ValueError(f"未找到支付配置: {appid}")
        if channel_key == 'wechat':
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
        elif channel_key == 'alipay':
            # 暂未测试验证 check_type = key 的使用情况
            check_type = getattr(config, 'check_type', 'cert')  # cert, key
            if check_type == 'cert':
                return DCAliPay(
                    appid=appid,
                    app_notify_url=None,
                    app_private_key_string=config['app_private_key'],
                    app_public_key_cert_string=config['app_public_cert'],
                    alipay_public_key_cert_string=config['platform_public_cert'],
                    alipay_root_cert_string=config['alipay_root_cert'],
                    sign_type=getattr(config, 'signType', 'RSA2'),
                    debug=getattr(config, 'sandbox', False),
                )
            else:
                return AliPay(
                    appid=appid,
                    app_notify_url=None,
                    app_private_key_string=config['app_private_key'],
                    alipay_public_key_string=config['platform_public_cert'],
                    sign_type=getattr(config, 'signType', 'RSA2'),
                    debug=getattr(config, 'sandbox', False),
                )
        else:
            raise ValueError(f"不支持当前支付方式: {channel_key}")

    def _get_payment_config(self, channel_key: str, appid: str):
        '''从配置文件获取支付配置'''

        # 需直接读取文件内容
        # app_public_key_cert_string = self._read_file_content(getattr(config, 'appCertPublicKey'))
        # alipay_public_key_cert_string = self._read_file_content(getattr(config, 'alipayCertPublicKey'))
        # alipay_root_cert_string = self._read_file_content(getattr(config, 'alipayRootCert'))

        configs = getattr(self.settings.PAY, channel_key.upper(), [])
        for config in configs:
            if channel_key == 'wechat':
                # 兼容小程序支付, 小程序支付回调返回的appid是小程序的appid, 而不是微信配置项里面的appid
                if config.appid == appid or config.miniAppId == appid or config.mchId == appid:
                    return config
            else:
                if config.appid == appid:
                    return config

        return None

    def _get_payment_config_from_cache(self, appid: str) -> dict:
        '''
        从缓存获取支付配置
        appid 可能是微信小程序的 appid, 所以在保存设置时，需要按 miniappid 保存一份
        '''
        with get_redis() as redis:
            config = json.loads(redis.hget(REDIS_PAYMENT_CONFIG, appid))
            if config["channel_key"] == "alipay":
                # 支付宝渠道时，需单独获取支付宝根证书
                config["alipay_root_cert"] = redis.hget(
                    REDIS_SYSTEM_OPTIONS_AUTOLOAD, "alipay_root_cert")

        return config

    def _add_key_header_footer(self, key_str: str, key_type: str):
        header = f"-----BEGIN {key_type}-----"
        footer = f"-----END {key_type}-----"
        return f"{header}\n{key_str.strip()}\n{footer}"

    def _read_file_content(self, file_path: str):
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as file:
            content = file.read()
        return content


# 创建 PaymentManager 单例
payment_manager = PaymentManager()
