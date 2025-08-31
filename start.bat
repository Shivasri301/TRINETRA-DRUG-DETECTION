@echo off
title Telegram Drug Monitor
echo ========================================
echo    Telegram Drug Monitor
echo    Hackathon Project 2024
echo ========================================
echo.

echo Checking Python installation...
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found! Starting application...
echo.

echo Installing/Updating dependencies...
py setup.py

echo.
echo Running health checks...
py health_check.py
if errorlevel 1 (
    echo WARNING: Some health checks failed
    echo Continuing anyway...
    timeout /t 3
)

echo.
echo Starting web server...
echo Open your browser to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

py app.py

pause
