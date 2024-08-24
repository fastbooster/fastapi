#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: city.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/29 14:32

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session
from app.models.cms import CityModel


def lists(pid: int) -> list[CityModel]:
    with get_session(read_only=True) as db:
        query = db.query(CityModel).filter(CityModel.pid == pid).order_by(asc(CityModel.id))
        results = query.all()
        return results
