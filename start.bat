@echo off
REM Windows startup script for DOU Blockchain

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment if not exists
if not exist venv (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run tests
python -m pytest tests\

REM Optional: Uncomment to run CLI
REM python cli.py

REM Keep window open
pause
