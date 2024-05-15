#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/4/16 22:30

from sqlalchemy import Column, Integer, String, Date, DECIMAL, PrimaryKeyConstraint, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "tz_report_user"

    employee_id = Column(String(50), primary_key=True, comment="工号")
    password_hash = Column(String(64), comment="密码")
    access_token = Column(String(64), unique=True, comment="密钥")
    last_login_at = Column(Integer, comment="最后登录时间")
    last_login_ip = Column(String(50), comment="最后登录IP")
    user_agent = Column(String(1000), comment="用户代理信息")


class ReportHistoryModel(Base):
    __tablename__ = 'tz_report_history'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    year = Column(SmallInteger, nullable=False, comment="年")
    month = Column(SmallInteger, nullable=False, comment="月")
    employee_id = Column(String(50), nullable=False, comment="工号")
    count_mz = Column(Integer, default=0, nullable=True, comment="门诊记录总数")
    count_zy = Column(Integer, default=0, nullable=True, comment="住院记录总数")
    je_sum = Column(DECIMAL(16, 4), default=0, nullable=True, comment="总分成金额")
    je_kd = Column(DECIMAL(16, 4), default=0, nullable=True, comment="开单分成")
    je_zx = Column(DECIMAL(16, 4), default=0, nullable=True, comment="执行分成")
    je_mzkd = Column(DECIMAL(16, 4), default=0, nullable=True, comment="门诊开单分成")
    je_mzzx = Column(DECIMAL(16, 4), default=0, nullable=True, comment="门诊执行分成")
    je_zykd = Column(DECIMAL(16, 4), default=0, nullable=True, comment="住院开单分成")
    je_zyzx = Column(DECIMAL(16, 4), default=0, nullable=True, comment="住院执行分成")
    begin_date = Column(String(10), nullable=True, comment="开始日期")
    end_date = Column(String(10), nullable=True, comment="结束日期")
    hash = Column(String(50), nullable=True, comment="HASH")
    permission_hash = Column(String(50), nullable=True, comment="权限HASH")
    create_at = Column(Integer, nullable=True, comment="创建时间")


class MzmxModel(Base):
    __tablename__ = 'mzmx'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(4), nullable=False)
    jkdate = Column(Date)
    ddate = Column(Date)
    num = Column(Integer, nullable=False)
    cOptype = Column(String(4), nullable=False)
    cInClass = Column(String(4), nullable=False)
    cChItem = Column(String(40))
    cChItemnum = Column(Integer)
    CR = Column(String(2))
    cDeptNum = Column(Integer)
    cPFDeptNum = Column(Integer)
    cDeptName = Column(String(150))
    cPFDeptName = Column(String(150))
    je = Column(DECIMAL(16, 4))
    jeDept = Column(DECIMAL(16, 8))
    jePFDept = Column(DECIMAL(16, 8))
    Price = Column(DECIMAL(16, 4))
    cPayMent = Column(String(1), nullable=False)
    cPayMentnum = Column(String(1), nullable=False)
    cPayItem = Column(String(1), nullable=False)
    cPayItemnum = Column(String(100))
    cPayItemName = Column(String(100))
    cCasher = Column(String(20))
    cCasherNum = Column(String(6), nullable=False)
    cdeptnumbm = Column(Integer)
    cdeptnamebm = Column(String(150))
    state = Column(String(1), nullable=False)
    kdys = Column(String(50))
    合并科室 = Column(String(100))
    hash = Column(String(50), nullable=False)
    isKfItem = Column(SmallInteger, default=0, nullable=False)


class MzmxHistoryModel(Base):
    __tablename__ = 'mzmx_history'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(4), nullable=False)
    jkdate = Column(Date)
    ddate = Column(Date)
    num = Column(Integer, nullable=False)
    cOptype = Column(String(4), nullable=False)
    cInClass = Column(String(4), nullable=False)
    cChItem = Column(String(40))
    cChItemnum = Column(Integer)
    CR = Column(String(2))
    cDeptNum = Column(Integer)
    cPFDeptNum = Column(Integer)
    cDeptName = Column(String(150))
    cPFDeptName = Column(String(150))
    je = Column(DECIMAL(16, 4))
    jeDept = Column(DECIMAL(16, 8))
    jePFDept = Column(DECIMAL(16, 8))
    Price = Column(DECIMAL(16, 4))
    cPayMent = Column(String(1), nullable=False)
    cPayMentnum = Column(String(1), nullable=False)
    cPayItem = Column(String(1), nullable=False)
    cPayItemnum = Column(String(100))
    cPayItemName = Column(String(100))
    cCasher = Column(String(20))
    cCasherNum = Column(String(6), nullable=False)
    cdeptnumbm = Column(Integer)
    cdeptnamebm = Column(String(150))
    state = Column(String(1), nullable=False)
    kdys = Column(String(50))
    合并科室 = Column(String(100))
    hash = Column(String(50), nullable=False)
    isKfItem = Column(SmallInteger, default=0, nullable=False)


class ZymxModel(Base):
    __tablename__ = 'zymx'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(4), nullable=False)
    jkdate = Column(Date)
    ddate = Column(Date)
    num = Column(Integer, nullable=False)
    cOptype = Column(String(4), nullable=False)
    cInClass = Column(String(4), nullable=False)
    cChItem = Column(String(40))
    cChItemnum = Column(Integer)
    CR = Column(String(2))
    cDeptNum = Column(Integer)
    cPFDeptNum = Column(Integer)
    cDeptName = Column(String(150))
    cPFDeptName = Column(String(150))
    je = Column(DECIMAL(16, 4))
    jeDept = Column(DECIMAL(16, 8))
    jePFDept = Column(DECIMAL(16, 8))
    Price = Column(DECIMAL(16, 4))
    cPayMent = Column(String(1), nullable=False)
    cPayMentnum = Column(String(1), nullable=False)
    cPayItem = Column(String(1), nullable=False)
    cPayItemnum = Column(String(20))
    cPayItemName = Column(String(100))
    cCasher = Column(String(20))
    cCasherNum = Column(String(8))
    state = Column(String(1), nullable=False)
    合并科室 = Column(String(100))
    hash = Column(String(50), nullable=False)
    开单医生 = Column(String(20), nullable=True)
    yzid = Column(Integer, nullable=True)
    isKfItem = Column(SmallInteger, default=0, nullable=False)


class ZymxHistoryModel(Base):
    __tablename__ = 'zymx_history'

    ID = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(4), nullable=False)
    jkdate = Column(Date)
    ddate = Column(Date)
    num = Column(Integer, nullable=False)
    cOptype = Column(String(4), nullable=False)
    cInClass = Column(String(4), nullable=False)
    cChItem = Column(String(40))
    cChItemnum = Column(Integer)
    CR = Column(String(2))
    cDeptNum = Column(Integer)
    cPFDeptNum = Column(Integer)
    cDeptName = Column(String(150))
    cPFDeptName = Column(String(150))
    je = Column(DECIMAL(16, 4))
    jeDept = Column(DECIMAL(16, 8))
    jePFDept = Column(DECIMAL(16, 8))
    Price = Column(DECIMAL(16, 4))
    cPayMent = Column(String(1), nullable=False)
    cPayMentnum = Column(String(1), nullable=False)
    cPayItem = Column(String(1), nullable=False)
    cPayItemnum = Column(String(20))
    cPayItemName = Column(String(100))
    cCasher = Column(String(20))
    cCasherNum = Column(String(8))
    state = Column(String(1), nullable=False)
    合并科室 = Column(String(100))
    hash = Column(String(50), nullable=False)
    开单医生 = Column(String(20), nullable=True)
    yzid = Column(Integer, nullable=True)
    isKfItem = Column(SmallInteger, default=0, nullable=False)
