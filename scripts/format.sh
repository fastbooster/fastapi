#!/bin/sh -e

set -x

mypy app
ruff check app scripts --fix
ruff format app scripts
