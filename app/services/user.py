#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: user.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 16:50

from app.core.mysql import get_session
from app.models.user import UserModel


def get_user(id: int) -> UserModel | None:
    with get_session() as db:
        user = db.query(UserModel).filter(UserModel.id == id).first()

    if user is not None:
        return user

    return None
