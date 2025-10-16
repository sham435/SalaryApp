#!/usr/bin/env python3
"""
Package SalaryApp for Windows .exe building
Creates a ZIP file with everything needed to build on Windows
"""

import os
import zipfile
from pathlib import Path

def create_package():
    print("=" * 60)
    print("  Packaging SalaryApp for Windows Build")
    print("=" * 60)
    print()

    # Files to include
    files_to_include = [
        'salary_calculator_gui.py',
        'requirements.txt',
        'build_exe.spec',
        'build_exe.py',
        'build_windows_exe.bat',
        'build_windows_exe.ps1',
        'GIVE_THIS_TO_WINDOWS_USER.txt',
        'QUICK_BUILD_README.txt',
        'installers/windows/jatan_icon.ico',
    ]

    output_file = 'SalaryApp_WindowsBuild_Package.zip'

    print(f"Creating: {output_file}")
    print()

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_include:
            if os.path.exists(file_path):
                zipf.write(file_path)
                print(f"  ✓ Added: {file_path}")
            else:
                print(f"  ✗ Missing: {file_path}")

    print()
    print("=" * 60)
    print("  Package Created Successfully!")
    print("=" * 60)
    print()
    print(f"📦 File: {output_file}")

    # Get file size
    file_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"📊 Size: {file_size:.2f} MB")
    print()
    print("📤 NEXT STEPS:")
    print("  1. Email this ZIP to yourself or colleague with Windows")
    print("  2. Extract on Windows PC")
    print("  3. Double-click: build_windows_exe.bat")
    print("  4. Get JatanSalaryApp.exe from dist folder")
    print()
    print("🎉 Done!")
    print()

if __name__ == "__main__":
    create_package()

