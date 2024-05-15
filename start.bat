@echo off

if exist "__pycache__" (
    echo deleting __pycache__
    rmdir /S /Q "__pycache__"
)

python -m venv venv

CALL "venv\Scripts\activate.bat"

python start.py

pause
