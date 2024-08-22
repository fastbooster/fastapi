#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: post_category.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/17 12:39

from sqlalchemy import text, Column, Integer, SmallInteger, String, DECIMAL, TIMESTAMP
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from app.models.base import Base, BaseMixin


class PostCategoryModel(Base, BaseMixin):
    __tablename__ = 'cms_post_category'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '文章分类'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(50), nullable=False, comment='名称', index=True)
    alias = Column(String(50), nullable=False, unique=True, index=True, comment='URL别名')
    keywords = Column(String(50), comment='关键字')
    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<PostCategoryModel(id={self.id}, name='{self.name}')>"


class PostModel(Base, BaseMixin):
    __tablename__ = 'cms_post'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '文章'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, server_default='0', index=True, comment='上级ID')
    category_id = Column(Integer, server_default='0', index=True, comment='分类ID')
    user_id = Column(Integer, server_default='0', index=True, comment='用户ID')

    title = Column(String(255), nullable=False, index=True, comment='标题')
    subtitle = Column(String(255), nullable=False, comment='副标题')
    keywords = Column(String(50), comment='关键字')
    digest = Column(String(50), comment='摘要')
    content = Column(MEDIUMTEXT, nullable=False, comment='内容')

    author = Column(String(50), comment='作者')
    editor = Column(String(50), comment='责编')
    source = Column(String(50), comment='来源')
    source_url = Column(String(1000), comment='来源URL')
    hero_image_url = Column(String(1000), comment='首图')

    price = Column(DECIMAL(10, 4), server_default='0', comment='价格')
    price_point = Column(Integer, server_default='0', comment='积分价格')

    view_num = Column(Integer, server_default='0', comment='浏览量')
    like_num = Column(Integer, server_default='0', comment='点赞量')
    collect_num = Column(Integer, server_default='0', comment='收藏量')
    comment_num = Column(Integer, server_default='0', comment='评论量')

    comment_status = Column(String(10), nullable=False, server_default='enabled', comment='评论状态: enabled/disabled')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<PostModel(id={self.id}, title='{self.title}')>"


class MediaModel(Base, BaseMixin):
    __tablename__ = 'cms_media'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '媒体文件'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    file_name = Column(String(255), comment='文件名称')
    file_type = Column(String(32), index=True, comment='文件类型')
    file_size = Column(Integer, comment='文件大小')
    file_path = Column(String(255), comment='文件路径')
    oss_url = Column(String(255), comment='OSS地址')
    op_user_id = Column(Integer, nullable=False, index=True, comment='操作员ID')
    op_user_name = Column(String(100), nullable=False, comment='操作员名称')
    related_type = Column(String(32), comment='关联类别')
    related_id = Column(Integer, server_default='0', index=True, comment='关联ID')
    view_num = Column(Integer, server_default='0', comment='浏览量/下载量')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    def __repr__(self):
        return f"<MediaModel(id={self.id}, oss_url='{self.oss_url}')>"


class CityModel(Base, BaseMixin):
    __tablename__ = 'cms_city'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '城市'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    pid = Column(Integer, nullable=False, server_default='0', index=True, comment='上级ID')
    name = Column(String(50), nullable=False, index=True, comment='地区名称')
    level = Column(SmallInteger, nullable=False, server_default='0', comment='等级:0省或直辖市,1市,2县')
    pinyin = Column(String(255), index=True, comment='拼音')
    prefix = Column(String(1), comment='拼音首字母缩写')
    weight = Column(Integer, server_default='0', comment='排序权重')
    is_hot = Column(SmallInteger, server_default='0', comment='是否为热门:0否,1是')

    def __repr__(self):
        return f"<CityModel(id={self.id}, name='{self.name}')>"


class AdspaceModel(Base, BaseMixin):
    __tablename__ = 'cms_adspace'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '广告位'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    name = Column(String(50), nullable=False, index=True, comment='广告名称')
    width = Column(Integer, server_default='0', comment='推荐宽度')
    height = Column(Integer, server_default='0', comment='推荐高度')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<AdCategoryModel(id={self.id}, name='{self.name}')>"


class BannerModel(Base, BaseMixin):
    __tablename__ = 'cms_banner'
    __table_args__ = {
        'mysql_charset': 'utf8mb4',
        'mysql_collate': 'utf8mb4_unicode_ci',
        'mysql_engine': 'InnoDB',
        'mariadb_engine': 'InnoDB',
        'comment': '广告资源'
    }

    id = Column(Integer, primary_key=True, autoincrement=True, comment='ID')
    adspace_id = Column(Integer, nullable=False, index=True, comment='广告位ID')
    position = Column(String(255), nullable=False, server_default='center', comment='位置:left|right|center|top|bottom')
    title = Column(String(255), nullable=False, comment='标题')
    subtitle = Column(String(255), comment='子标题')
    description = Column(String(255), comment='描述')
    content = Column(String(500), comment='详细内容')
    pc_cover = Column(String(255), comment='PC端封面图')
    mobile_cover = Column(String(255), comment='移动端封面图')
    button_title = Column(String(255), comment='按钮标题')
    button_url = Column(String(255), comment='按钮地址')
    status = Column(String(10), nullable=False, server_default='enabled', comment='状态: enabled/disabled')
    asc_sort_order = Column(Integer, server_default='0', comment='排序')
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    def __repr__(self):
        return f"<AdModel(id={self.id}, title='{self.title}')>"
