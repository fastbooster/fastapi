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

root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(root_path)

template_path = os.path.join(root_path, 'app/gen/templates')
model_path = os.path.join(root_path, 'app/models')
schema_path = os.path.join(root_path, 'app/schemas')
service_path = os.path.join(root_path, 'app/services')
backend_route_path = os.path.join(root_path, 'app/api/backend')

from app.utils.helper import camel_to_snake, pluralize


def generate_schema(module_name: str, model_name: str):
    pass


def generate_service(module_name: str, model_name: str):
    template_file = os.path.join(template_path, 'service.py.mako')
    snake_name = camel_to_snake(model_name.rstrip("Model"))
    file_name = f'{snake_name}.py'
    service_file = os.path.join(service_path, file_name)
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    model = model_name.rstrip('Model')
    route = pluralize(model).lower()

    module = importlib.import_module(f'app.models.{module_name}')
    model_class = getattr(module, model_name)
    comment = model_class.__table_args__[-1]['comment']
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
    logger.info(f'生成服务 {service_file.replace(root_path, '')} 成功')


def generate_route(module_name: str, model_name: str):
    template_file = os.path.join(template_path, 'route.py.mako')
    snake_name = camel_to_snake(model_name.rstrip("Model"))
    file_name = f'{snake_name}.py'
    backend_route_file = os.path.join(backend_route_path, file_name)
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    model = model_name.rstrip('Model')
    route = pluralize(model).lower()

    module = importlib.import_module(f'app.models.{module_name}')
    model_class = getattr(module, model_name)
    comment = model_class.__table_args__[-1]['comment']
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
    logger.info(f'生成路由 {backend_route_file.replace(root_path, '')} 成功')


def main() -> None:
    parser = argparse.ArgumentParser(description="FastBooster Generator")
    parser.add_argument("--name", type=str, help='模型名称, 例如: user.UserModel', required=True)
    parser.add_argument("--target", type=str, default='all', choices=('schema', 'service', 'route', 'all'),
                        help='生成模块')

    args = parser.parse_args()

    tmp = args.name.split('.')
    if len(tmp) != 2:
        logger.error('模型名称格式错误')
        return
    module_name, model_name = tmp
    module_file = os.path.join(model_path, f'{module_name}.py')
    if not os.path.exists(module_file):
        logger.error(f'模型文件 {module_file} 不存在')
        return
    if not model_name.endswith('Model'):
        logger.error(f'模型名称 {model_name} 错误, 必须以 Model 结尾')
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
