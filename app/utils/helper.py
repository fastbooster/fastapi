#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: helper.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import calendar
import datetime


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
    raise TypeError("Type not serializable")


def model_to_dict(instance):
    return {c.key: getattr(instance, c.key) for c in instance.__table__.columns}
