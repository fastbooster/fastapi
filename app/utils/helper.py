#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: helper.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import calendar
import datetime
import re
import os


def get_root_path():
    '''获取项目根目录'''
    abspath = os.path.dirname(os.path.abspath(__file__))    # 当前文件的绝对路径
    return abspath.replace(f'{os.path.sep}app{os.path.sep}utils', '') # 剔除多余部分 /app/utils 并返回


def get_last_day_of_month_by_year(year: int) -> list:
    if year < 1000 or year > 9999:
        raise ValueError("只支持 1000~9999 之间的年份")

    month_days = {}
    for month in range(1, 13):
        _, days_in_month = calendar.monthrange(year, month)
        month_days[month] = days_in_month

    return ["{:04d}-{:02d}-{:02d}".format(year, month, days) for month, days in month_days.items()]


def serialize_datetime(obj):
    """JSON序列化datetime类时间"""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, str):
        return obj
    raise TypeError("Type not serializable")


def camel_to_snake(name):
    # 找到大写字母并在前面加上下划线，然后将其转换为小写
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 处理连续的大写字母
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(name):
    # 分割字符串并将每个单词首字母大写，然后合并
    return ''.join(word.capitalize() for word in name.split('_'))


def pluralize(word: str) -> str:
    # 不规则复数
    irregulars = {
        "man": "men",
        "woman": "women",
        "child": "children",
        "tooth": "teeth",
        "foot": "feet",
        "mouse": "mice",
        "goose": "geese",
        "person": "people"
    }

    # 如果单词在不规则复数词典中，直接返回不规则复数
    if word in irregulars:
        return irregulars[word]

    # 规则 1: 以 s, x, z, ch, sh 结尾，加 es
    if re.search(r'(s|x|z|ch|sh)$', word):
        return word + 'es'

    # 规则 2: 以辅音字母加 y 结尾，将 y 变为 ies
    elif re.search(r'[^aeiou]y$', word):
        return word[:-1] + 'ies'

    # 规则 3: 以 f 或 fe 结尾，将 f 变为 ves
    elif re.search(r'(f|fe)$', word):
        return re.sub(r'(f|fe)$', 'ves', word)

    # 规则 4: 其他情况下，直接加 s
    else:
        return word + 's'
