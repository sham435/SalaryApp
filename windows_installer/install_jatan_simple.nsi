; ============================================
; Jatan Salary Management System
; Simple Windows Installer (NSIS)
; ============================================

!include "MUI2.nsh"

; Basic Information
Name "Jatan Salary System"
OutFile "Jatan_Salary_Installer.exe"
InstallDir "$PROGRAMFILES64\JatanSalary"
RequestExecutionLevel admin

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "Jatan Salary Management System"
!define MUI_WELCOMEPAGE_TEXT "This will install the Jatan Salary Management System.$\r$\n$\r$\nRequires: Docker Desktop for Windows$\r$\n$\r$\nClick Next to continue."

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Language
!insertmacro MUI_LANGUAGE "English"

; Installation Section
Section "Install"
  SetOutPath $INSTDIR

  ; Copy all files
  File /r "docker-compose.production.yml"
  File /r ".env"
  File /r "Dockerfile"
  File /r "requirements.txt"
  File /r "*.py"
  File /r "monitoring"
  File /r "scripts"
  File /r "installers"

  ; Create batch files
  FileOpen $0 "$INSTDIR\Start_Jatan.bat" w
  FileWrite $0 "@echo off$\r$\n"
  FileWrite $0 "cd /D $\"$INSTDIR$\"$\r$\n"
  FileWrite $0 "echo Starting Jatan Salary System...$\r$\n"
  FileWrite $0 "docker compose -f docker-compose.production.yml --profile monitoring up -d$\r$\n"
  FileWrite $0 "timeout /t 5$\r$\n"
  FileWrite $0 "start http://localhost:3000$\r$\n"
  FileWrite $0 "pause$\r$\n"
  FileClose $0

  FileOpen $0 "$INSTDIR\Stop_Jatan.bat" w
  FileWrite $0 "@echo off$\r$\n"
  FileWrite $0 "cd /D $\"$INSTDIR$\"$\r$\n"
  FileWrite $0 "docker compose -f docker-compose.production.yml down$\r$\n"
  FileWrite $0 "pause$\r$\n"
  FileClose $0

  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\Jatan Salary System.lnk" "$INSTDIR\Start_Jatan.bat"

  ; Create Start Menu folder
  CreateDirectory "$SMPROGRAMS\Jatan Salary System"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Start Jatan.lnk" "$INSTDIR\Start_Jatan.bat"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Stop Jatan.lnk" "$INSTDIR\Stop_Jatan.bat"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Open Grafana.lnk" "http://localhost:3000"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Registry entries
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanSalary" "DisplayName" "Jatan Salary Management System"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanSalary" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanSalary" "DisplayVersion" "3.2.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanSalary" "Publisher" "Jatan Jewellery FZ.C"

  MessageBox MB_OK "Installation complete!$\r$\n$\r$\nUse desktop shortcut to start.$\r$\n$\r$\nNote: Docker Desktop must be running."

SectionEnd

; Uninstaller
Section "Uninstall"
  ExecWait 'cmd /C "cd /D $INSTDIR && docker compose -f docker-compose.production.yml down -v"'
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  Delete "$DESKTOP\Jatan Salary System.lnk"
  RMDir /r "$SMPROGRAMS\Jatan Salary System"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanSalary"
SectionEnd


