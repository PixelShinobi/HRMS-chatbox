@echo off
echo ================================================
echo   HRMS AI Chatbot - Backend Startup Script
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if .env exists
if not exist ".env" (
    echo .env file not found! Creating from .env.example...
    copy .env.example .env
    echo Please edit .env file if needed.
    echo.
)

REM Install/update dependencies
echo Installing/updating dependencies...
pip install -r requirements.txt -q
echo Dependencies installed!
echo.

REM Start the server
echo ================================================
echo   Starting FastAPI Backend Server...
echo   Server will be available at: http://localhost:8000
echo ================================================
echo.
python main.py
