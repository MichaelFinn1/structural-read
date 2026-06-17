@echo off
setlocal

if "%~1"=="" (
  echo.
  echo Drag a log file or folder onto this file, or run:
  echo Run-LogStructure.Drop.bat "C:\path\to\logs"
  echo.
  pause
  exit /b 1
)

set TARGET=%~1
set SCRIPT_DIR=%~dp0

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Run-LogStructureSurface.V0.ps1" -Path "%TARGET%"

echo.
echo Log Structure Surface complete.
echo.
pause
