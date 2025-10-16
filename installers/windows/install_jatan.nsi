; ============================================
; Jatan Jewellery - Salary Management System
; Windows Installer Script (NSIS)
; ============================================

!include "MUI2.nsh"

; Installer Information
Name "Jatan Salary Management System"
OutFile "Jatan_Stack_Setup.exe"
InstallDir "$PROGRAMFILES64\JatanStack"
RequestExecutionLevel admin

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "jatan_icon.ico"
!define MUI_WELCOMEPAGE_TITLE "Welcome to Jatan Salary Management System Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will install the complete enterprise stack including PostgreSQL, Redis, RabbitMQ, Celery, and monitoring tools.$\r$\n$\r$\nDocker Desktop is required to run this application.$\r$\n$\r$\nClick Next to continue."

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; ============================================
; Installer Sections
; ============================================

Section "Install" SecInstall
  ; Set output path
  SetOutPath $INSTDIR

  ; Copy files
  File /r "jatan_stack.tar"
  File /r "docker-compose.production.yml"
  File /r ".env.example"
  File /r "start_stack.bat"
  File /r "stop_stack.bat"
  File /r "view_grafana.bat"
  File /r "monitoring\*.*"

  ; Check Docker Desktop
  DetailPrint "Checking Docker Desktop..."
  ExecWait 'docker --version' $0
  ${If} $0 != 0
    MessageBox MB_OK "Docker Desktop is not installed or not running. Please install Docker Desktop from https://www.docker.com/products/docker-desktop and try again."
    Abort
  ${EndIf}

  ; Load Docker images
  DetailPrint "Loading Docker images (this may take a few minutes)..."
  ExecWait 'cmd /C "cd /D $INSTDIR && docker load -i jatan_stack.tar"' $1
  ${If} $1 != 0
    MessageBox MB_OK "Failed to load Docker images. Please check Docker Desktop is running."
  ${EndIf}

  ; Create .env if not exists
  IfFileExists "$INSTDIR\.env" +2 0
    CopyFiles "$INSTDIR\.env.example" "$INSTDIR\.env"

  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\Jatan Salary System.lnk" "$INSTDIR\start_stack.bat" "" "$INSTDIR\jatan_icon.ico"

  ; Create Start Menu folder
  CreateDirectory "$SMPROGRAMS\Jatan Salary System"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Start Stack.lnk" "$INSTDIR\start_stack.bat"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Stop Stack.lnk" "$INSTDIR\stop_stack.bat"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Open Grafana.lnk" "$INSTDIR\view_grafana.bat"
  CreateShortcut "$SMPROGRAMS\Jatan Salary System\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; Write registry keys
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack" "DisplayName" "Jatan Salary Management System"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack" "DisplayIcon" "$INSTDIR\jatan_icon.ico"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack" "DisplayVersion" "3.1.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack" "Publisher" "Jatan Jewellery FZ.C"

  MessageBox MB_OK "Installation complete! Use the desktop shortcut to start the application."

SectionEnd

; ============================================
; Uninstaller Section
; ============================================

Section "Uninstall"
  ; Stop containers
  ExecWait 'cmd /C "cd /D $INSTDIR && docker compose -f docker-compose.production.yml down -v"'

  ; Remove Docker images (optional)
  MessageBox MB_YESNO "Do you want to remove Docker images? (This will save disk space)" IDYES RemoveImages IDNO SkipImages
  RemoveImages:
    ExecWait 'cmd /C "docker rmi jatan_salary_app jatan_postgres jatan_redis jatan_rabbitmq jatan_grafana jatan_prometheus"'
  SkipImages:

  ; Remove files
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"

  ; Remove shortcuts
  Delete "$DESKTOP\Jatan Salary System.lnk"
  RMDir /r "$SMPROGRAMS\Jatan Salary System"

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\JatanStack"

SectionEnd


