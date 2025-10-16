@echo off
echo ========================================
echo Building Jatan Salary App Windows EXE
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Step 2: Building EXE with PyInstaller...
pyinstaller build_exe.spec --clean --noconfirm

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The executable is located at:
echo   dist\JatanSalaryApp.exe
echo.
echo You can now distribute this .exe file to users.
echo Users don't need Python installed to run it.
echo.
pause

