@echo off
REM ============================================
REM Jatan Salary Management System - Startup
REM ============================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Jatan Salary Management System                       ║
echo ║  Starting Full Stack...                               ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Change to installation directory
cd /D "%~dp0"

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [INFO] Docker is running
echo [INFO] Starting services...
echo.

REM Start stack
docker compose -f docker-compose.production.yml --profile monitoring --profile admin up -d

if errorlevel 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════╗
    echo ║  ✅ Stack started successfully!                        ║
    echo ╚════════════════════════════════════════════════════════╝
    echo.
    echo Access URLs:
    echo   - Grafana:   http://localhost:3000
    echo   - RabbitMQ:  http://localhost:15672
    echo   - Flower:    http://localhost:5555
    echo   - PgAdmin:   http://localhost:5050
    echo.
    echo Opening Grafana in your browser...
    timeout /t 3 >nul
    start http://localhost:3000
) else (
    echo.
    echo [ERROR] Failed to start stack
    echo Check Docker Desktop and try again
)

echo.
pause


