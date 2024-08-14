#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: log.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/26 15:44

import os
import sys

import loguru

from app.constants.constants import RUNTIME_PATH


def get_logger():
    # 文件的命名
    log_name = '{time:YYYY-MM-DD}.log'
    log_path = os.path.join(RUNTIME_PATH, 'log')
    custom_logger = loguru.logger
    # 清空所有设置
    custom_logger.remove()
    # 判断日志文件夹是否存在，不存则创建
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    # 日志输出格式
    # formatter = '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level}: {message}'
    # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
    custom_logger.add(sys.stdout,
                      format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '  # 时间
                             '{process.name} | '  # 进程名
                             '{thread.name} | '  # 线程名
                             '<cyan>{module}</cyan>.<cyan>{function}</cyan>'  # 模块名.方法名
                             ':<cyan>{line}</cyan> | '  # 行号
                             '<level>{level}</level>: '  # 等级
                             '{message} {extra}',  # 日志内容
                      )
    # 日志写入文件
    custom_logger.add(os.path.join(log_path, log_name),  # 写入目录指定文件
                      format='{time:YYYY-MM-DD HH:mm:ss.SSS} - '  # 时间
                             '{process.name} | '  # 进程名
                             '{thread.name} | '  # 线程名
                             '{module}.{function}:{line} | '  # 模块名.方法名:行号
                             '{level}: {message} {extra}',  # 等级 日志内容
                      encoding='utf-8',
                      retention='7 days',  # 设置历史保留时长
                      backtrace=True,  # 回溯
                      diagnose=True,  # 诊断
                      enqueue=True,  # 异步写入
                      rotation='00:00',  # 每日更新时间
                      # rotation='5kb',  # 切割，设置文件大小，rotation='12:00'，rotation='1 week'
                      # filter='my_module'  # 过滤模块
                      # compression='zip'   # 文件压缩
                      )
    return custom_logger


class Log:
    log = None

    def __getattr__(self, name):
        # 调用log时再初始化，为了加载最新的env
        if self.__class__.log is None:
            self.__class__.log = get_logger()
        return getattr(self.__class__.log, name)

    @property
    def debug(self):
        return self.__class__.log.debug

    @property
    def info(self):
        return self.__class__.log.info

    @property
    def warning(self):
        return self.__class__.log.warning

    @property
    def exception(self):
        return self.__class__.log.exception

    @property
    def error(self):
        return self.__class__.log.error

    @property
    def critical(self):
        return self.__class__.log.critical


logger = Log()
