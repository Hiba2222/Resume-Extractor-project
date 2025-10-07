@echo off
setlocal enabledelayedexpansion

echo ================================================
echo           CV EXTRACTOR LAUNCHER               
echo ================================================

:: Main menu
:menu
echo.
echo Choose an option:
echo 1. Start with Docker (recommended)
echo 2. Start with Python directly
echo 3. Stop running Docker containers
echo 4. Exit

set /p choice="Enter your choice [1-4]: "

if "%choice%"=="1" goto :start_with_docker
if "%choice%"=="2" goto :start_with_python
if "%choice%"=="3" goto :stop_docker
if "%choice%"=="4" (
    echo Exiting. Goodbye!
    exit /b 0
)

echo Invalid choice. Please try again.
goto :menu

:: Function to check if Docker is running
:check_docker
docker info > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not running.
    echo Please start Docker Desktop and try again.
    goto :menu
)
goto :eof

:: Function to start with Docker
:start_with_docker
echo Starting CV Extractor with Docker...
call :check_docker
if %ERRORLEVEL% neq 0 goto :menu

echo Building and starting containers...
docker-compose up --build
goto :menu

:: Function to start with Python directly
:start_with_python
echo Starting CV Extractor with Python...
echo Checking for Python...

where python > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found.
    goto :menu
)

echo Checking for required packages...
if exist requirements.txt (
    python -m pip install -r requirements.txt
)

echo Starting the application...
python run_web.py
goto :menu

:: Function to stop Docker containers
:stop_docker
echo Stopping Docker containers...
docker-compose down
echo Docker containers stopped.
goto :menu

:eof 