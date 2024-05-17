#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: init_permissions.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 09:39

from app.core.mysql import get_session
from app.models.user import UserModel

with get_session() as db:
    user = db.query(UserModel).first()
    print(user)
