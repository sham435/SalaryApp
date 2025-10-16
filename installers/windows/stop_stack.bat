@echo off
REM ============================================
REM Jatan Salary Management System - Shutdown
REM ============================================

echo.
echo Stopping Jatan Stack...
echo.

cd /D "%~dp0"

docker compose -f docker-compose.production.yml down

echo.
echo ✅ Stack stopped successfully
echo.
pause


