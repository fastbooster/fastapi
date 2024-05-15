#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# File: start.py
# Author: Super Junior
# Email: easelify@gmail.com
# Time: 2024/05/15 21:12

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

RELOAD = False if os.getenv("RUNTIME_MODE") == "PROD" else True
RUNTIME_PORT = int(str(os.getenv("RUNTIME_PORT")))
WORKERS = int(str(os.getenv("WORKERS")))

if __name__ == "__main__":
    if not RELOAD:
        uvicorn.run("main:app", host="0.0.0.0", port=RUNTIME_PORT, workers=WORKERS)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=RUNTIME_PORT, reload=True)
