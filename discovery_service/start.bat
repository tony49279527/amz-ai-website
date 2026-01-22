@echo off
REM Quick start script for Product Discovery Service

echo ========================================
echo Product Discovery Service - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please create .env file with your OPENROUTER_API_KEY
    echo You can copy .env.example and fill in your keys
    echo.
    pause
    exit /b 1
)

echo [1/2] Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m discovery_service.main

pause
