#!/usr/bin/env python
# -*- coding:utf-8 -*-
# File: main.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/8/20 13:17


import argparse
import importlib
import os
import sys
from datetime import datetime

from loguru import logger
from mako.template import Template
from sqlalchemy import inspect

root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(root_path)

template_path = os.path.join(root_path, 'app/gen/templates')
model_path = os.path.join(root_path, 'app/models')
schema_path = os.path.join(root_path, 'app/schemas')
service_path = os.path.join(root_path, 'app/services')
backend_route_path = os.path.join(root_path, 'app/api/backend')

from app.utils.helper import camel_to_snake, pluralize


def generate_schema(module_name: str, model_name: str):
    template_file = os.path.join(template_path, 'schema.py.mako')
    snake_name = camel_to_snake(model_name.replace("Model", ''))
    file_name = f'{snake_name}.py'
    schema_file = os.path.join(schema_path, file_name)
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    model = model_name.replace('Model', '')
    route = pluralize(snake_name).lower()

    module = importlib.import_module(f'app.models.{module_name}')
    model_class = getattr(module, model_name)
    if isinstance(model_class.__table_args__, tuple):
        comment = model_class.__table_args__[-1]['comment']
    elif isinstance(model_class.__table_args__, dict):
        comment = model_class.__table_args__['comment']
    else:
        logger.error('未知的表属性，请检查模型设置')
        return
    name = comment if comment else model

    maps = {
        'int': 'int',
        'integer': 'int',
        'tinyint': 'int',
        'smallint': 'int',
        'mediumint': 'int',
        'bigint': 'int',
        'bit': 'int',
        'year': 'int',
        'bool': 'bool',
        'boolean': 'bool',

        'float': 'float',
        'double': 'float',
        'real': 'float',

        'decimal': 'Decimal',
        'numeric': 'Decimal',

        'date': 'datetime.date',
        'time': 'datetime.time',
        'datetime': 'datetime',
        'timestamp': 'datetime',

        'char': 'str',
        'varchar': 'str',
        'tinytext': 'str',
        'text': 'str',
        'mediumtext': 'str',
        'longtext': 'str',
        'enum': 'str',
        'set': 'str',
        'json': 'str',
        'xml': 'str',

        'binary': 'bytes',
        'varbinary': 'bytes',
        'tinyblob': 'bytes',
        'blob': 'bytes',
        'mediumblob': 'bytes',
        'longblob': 'bytes',
    }

    inspector = inspect(model_class)
    columns = []
    for column in inspector.columns:
        if column.name in ('id', 'created_at', 'updated_at'):
            continue
        column_type = str(column.type).split("(")[0].lower()
        columns.append({
            'name': column.name,
            'type': maps[column_type] if column_type in maps else 'str',
            'comment': column.comment,
        })

    with open(template_file, 'r', encoding='utf-8') as f:
        content = Template(f.read()).render(
            module_name=module_name,  # system_option
            model_name=model_name,  # SystemOptionModel
            model=model,  # SystemOption
            route=route,  # system_options
            snake_name=snake_name,  # system_option
            file_name=file_name,  # system_options.py
            name=name,  # 系统选项
            create_time=create_time,  # 2024-08-19 16:37
            columns=columns
        )
        with open(schema_file, 'w', encoding='utf-8') as wf:
            wf.write(content)
    logger.info(f'{schema_file.replace(root_path, '')}...生成成功')


def generate_service(module_name: str, model_name: str):
    template_file = os.path.join(template_path, 'service.py.mako')
    snake_name = camel_to_snake(model_name.replace("Model", ''))
    file_name = f'{snake_name}.py'
    service_file = os.path.join(service_path, file_name)
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    model = model_name.replace('Model', '')
    route = pluralize(snake_name).lower()

    module = importlib.import_module(f'app.models.{module_name}')
    model_class = getattr(module, model_name)
    if isinstance(model_class.__table_args__, tuple):
        comment = model_class.__table_args__[-1]['comment']
    elif isinstance(model_class.__table_args__, dict):
        comment = model_class.__table_args__['comment']
    else:
        logger.error('未知的表属性，请检查模型设置')
        return
    name = comment if comment else model

    with open(template_file, 'r', encoding='utf-8') as f:
        content = Template(f.read()).render(
            module_name=module_name,  # system_option
            model_name=model_name,  # SystemOptionModel
            model=model,  # SystemOption
            route=route,  # system_options
            snake_name=snake_name,  # system_option
            file_name=file_name,  # system_options.py
            name=name,  # 系统选项
            create_time=create_time,  # 2024-08-19 16:37
        )
        with open(service_file, 'w', encoding='utf-8') as wf:
            wf.write(content)
    logger.info(f'{service_file.replace(root_path, '')}...生成成功')


def generate_route(module_name: str, model_name: str):
    template_file = os.path.join(template_path, 'route.py.mako')
    snake_name = camel_to_snake(model_name.replace("Model", ''))
    file_name = f'{snake_name}.py'
    backend_route_file = os.path.join(backend_route_path, file_name)
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    model = model_name.replace('Model', '')
    route = pluralize(snake_name).lower()

    module = importlib.import_module(f'app.models.{module_name}')
    model_class = getattr(module, model_name)
    if isinstance(model_class.__table_args__, tuple):
        comment = model_class.__table_args__[-1]['comment']
    elif isinstance(model_class.__table_args__, dict):
        comment = model_class.__table_args__['comment']
    else:
        logger.error('未知的表属性，请检查模型设置')
        return
    name = comment if comment else model

    with open(template_file, 'r', encoding='utf-8') as f:
        content = Template(f.read()).render(
            module_name=module_name,  # system_option
            model_name=model_name,  # SystemOptionModel
            model=model,  # SystemOption
            route=route,  # system_options
            snake_name=snake_name,  # system_option
            file_name=file_name,  # system_options.py
            name=name,  # 系统选项
            create_time=create_time,  # 2024-08-19 16:37
        )
        with open(backend_route_file, 'w', encoding='utf-8') as wf:
            wf.write(content)
    logger.info(f'{backend_route_file.replace(root_path, '')}...生成成功')


def main() -> None:
    parser = argparse.ArgumentParser(description="FastBooster Generator")
    parser.add_argument('-n', '--name', type=str, help='model name, e.g.: user.UserModel', required=True)
    parser.add_argument('-t', '--target', type=str, default='all', choices=('schema', 'service', 'route', 'all'),
                        help='generate target, default: all')

    args = parser.parse_args()

    tmp = args.name.split('.')
    if len(tmp) != 2:
        logger.error('model name error, e.g.: user.UserModel')
        return
    module_name, model_name = tmp
    module_file = os.path.join(model_path, f'{module_name}.py')
    if not os.path.exists(module_file):
        logger.error(f'model name {module_name} not exists')
        return
    if not model_name.endswith('Model'):
        logger.error(f'model name {model_name} not endswith "Model"')
        return

    match args.target:
        case 'schema':
            generate_schema(module_name, model_name)
        case 'service':
            generate_service(module_name, model_name)
        case 'route':
            generate_route(module_name, model_name)
        case 'all':
            generate_schema(module_name, model_name)
            generate_service(module_name, model_name)
            generate_route(module_name, model_name)
        case _:
            logger.error(f'{args.target} is not supported')


if __name__ == "__main__":
    main()
