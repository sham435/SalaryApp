#!/usr/bin/env python3
"""
Simple Python script to build Windows .exe for Jatan Salary App
Run this on a Windows machine with: python build_exe.py
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    print("\n" + "="*50)
    print(f"  {text}")
    print("="*50 + "\n")

def check_python():
    """Check Python version"""
    print(f"✓ Python {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ ERROR: Python 3.8 or higher required")
        return False
    return True

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    
    packages = [
        'pyinstaller',
        'pandas>=1.5.0',
        'reportlab>=4.0.0',
        'openpyxl>=3.0.0',
    ]
    
    for package in packages:
        print(f"  Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
            print(f"  ✓ {package} installed")
        except subprocess.CalledProcessError:
            print(f"  ✗ Failed to install {package}")
            return False
    
    return True

def build_exe():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Check if spec file exists
    if os.path.exists('build_exe.spec'):
        print("  Using build_exe.spec configuration...")
        cmd = [sys.executable, '-m', 'PyInstaller', 'build_exe.spec', '--clean', '--noconfirm']
    else:
        print("  Using default configuration...")
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'JatanSalaryApp',
            'salary_calculator_gui.py'
        ]
    
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        print("✗ Build failed!")
        return False

def main():
    print_header("Jatan Salary App - Windows EXE Builder")
    
    # Check OS
    current_os = platform.system()
    print(f"Current OS: {current_os}")
    
    if current_os != "Windows":
        print("\n⚠️  WARNING: You are not on Windows!")
        print("This will create an executable for your current platform.")
        print("For Windows .exe, please run this script on a Windows machine.\n")
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Build cancelled.")
            return
    
    # Check Python version
    if not check_python():
        input("Press Enter to exit...")
        return
    
    # Install requirements
    print_header("Step 1: Installing Dependencies")
    if not install_requirements():
        print("\n✗ Failed to install requirements!")
        input("Press Enter to exit...")
        return
    
    # Build executable
    print_header("Step 2: Building Executable")
    if not build_exe():
        print("\n✗ Build failed!")
        input("Press Enter to exit...")
        return
    
    # Success!
    print_header("Build Complete!")
    
    exe_name = "JatanSalaryApp.exe" if current_os == "Windows" else "JatanSalaryApp"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # Convert to MB
        print(f"✓ Executable created successfully!")
        print(f"  Location: {exe_path}")
        print(f"  Size: {file_size:.2f} MB")
        print(f"\n✓ Ready to distribute!")
        
        if current_os == "Windows":
            print(f"\nYou can now share '{exe_name}' with users.")
            print("No Python installation required on target machines.")
    else:
        print(f"✗ Executable not found at: {exe_path}")
    
    print("\n" + "="*50)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

