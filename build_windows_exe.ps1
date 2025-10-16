# PowerShell script to build Windows EXE for Jatan Salary App

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Jatan Salary App Windows EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Installing required packages..." -ForegroundColor Yellow
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet

Write-Host "✓ Packages installed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Building EXE with PyInstaller..." -ForegroundColor Yellow
pyinstaller build_exe.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Build Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The executable is located at:" -ForegroundColor Cyan
    Write-Host "  dist\JatanSalaryApp.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "You can now distribute this .exe file to users." -ForegroundColor Green
    Write-Host "Users don't need Python installed to run it." -ForegroundColor Green
    Write-Host ""
    
    # Check file size
    $exePath = "dist\JatanSalaryApp.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"

