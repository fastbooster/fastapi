#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: city.py
# Author: DON
# Email: qiuyutang@qq.com
# Time: 2024/5/29 14:32

from sqlalchemy.sql.expression import asc

from app.core.mysql import get_session
from app.models.cms import CityModel


def get_city_list(pid: int) -> list[CityModel]:
    with get_session() as db:
        query = db.query(CityModel).filter(CityModel.pid == pid, CityModel.status == 1).order_by(asc(CityModel.id))
        results = query.all()

    return results
