# 🪟 How to Create .exe Installer for Windows

**Simple guide to create Jatan_Salary_Installer.exe**

---

## 🎯 Quick Method (2 Steps)

### Step 1: Install NSIS on Windows

Download NSIS from: https://nsis.sourceforge.io/Download

Or use Chocolatey:
```powershell
choco install nsis
```

### Step 2: Build the .exe

**On Windows:**
```powershell
# Copy SalaryApp folder to Windows
# Navigate to windows_installer folder
cd C:\path\to\SalaryApp\windows_installer

# Right-click install_jatan_simple.nsi
# Select "Compile NSIS Script"

# Or from command line:
makensis install_jatan_simple.nsi
```

**Output**: `Jatan_Salary_Installer.exe` (~50-100 MB without Docker images)

---

## 🚀 What the .exe Does

When users run the installer:

1. ✅ Extracts files to `C:\Program Files\JatanSalary`
2. ✅ Copies all configuration files
3. ✅ Creates desktop shortcut
4. ✅ Creates Start Menu entries:
   - Start Jatan
   - Stop Jatan
   - Open Grafana
   - Uninstall
5. ✅ Sets up .env with password `1234`

When users click "Start Jatan":
- Checks if Docker Desktop is running
- Runs: `docker compose up -d`
- Docker automatically pulls all images
- Opens Grafana at http://localhost:3000

---

## 📦 Alternative: Self-Extracting ZIP

If you don't have NSIS, create a simple self-extracting archive:

### Using 7-Zip (Easier)

1. **Install 7-Zip**: https://www.7-zip.org/

2. **Create archive**:
```powershell
# Copy entire SalaryApp folder to Windows

# Right-click SalaryApp folder
# 7-Zip → Add to archive
# Archive format: 7z
# Check "Create SFX archive"
# Archive name: Jatan_Salary_Setup.exe
```

3. **Add installer script**:
Create `install.bat` in SalaryApp folder:
```batch
@echo off
echo Installing Jatan Salary System...
xcopy /E /I /Y "%~dp0" "C:\JatanSalary\"
echo.
echo Installation complete!
echo Run: C:\JatanSalary\Start_Jatan.bat
pause
```

---

## 📋 Files Included in .exe

The installer includes:
- `docker-compose.production.yml`
- `.env` (with DB_PASSWORD=1234)
- `Dockerfile`
- `requirements.txt`
- All Python files (*.py)
- `monitoring/` folder
- `scripts/` folder

**Total size**: ~10-20 MB (without Docker images)

Docker images (~2 GB) are downloaded automatically on first run.

---

## 🎯 Distribution

### Option 1: With Internet (Recommended)
- ✅ Small .exe file (10-20 MB)
- ✅ Downloads Docker images on demand
- ✅ Always gets latest images
- ✅ Easy to update

### Option 2: Offline (Advanced)
- Include `jatan_stack.tar` in installer
- .exe becomes very large (~2-3 GB)
- Can install without internet
- More complex to build

---

## 🔨 Build Command Summary

**On Windows machine:**

```powershell
# 1. Install NSIS
choco install nsis

# 2. Navigate to folder
cd C:\path\to\SalaryApp\windows_installer

# 3. Build .exe
makensis install_jatan_simple.nsi

# 4. Output
# → Jatan_Salary_Installer.exe created!
```

**Or use 7-Zip:**
```powershell
# Right-click SalaryApp folder
# 7-Zip → Add to archive → Create SFX archive
# → Jatan_Salary_Setup.exe created!
```

---

## ✅ Done!

The .exe will be ready for distribution. Users just:
1. Double-click `Jatan_Salary_Installer.exe`
2. Follow wizard
3. Click desktop shortcut to start
4. Grafana opens automatically

---

**File**: `install_jatan_simple.nsi` (ready to compile)
**Output**: `Jatan_Salary_Installer.exe`
**Size**: 10-20 MB (without images) or 2-3 GB (with images)

🎉 **Ready to build on Windows!**


