@echo off
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%\frontend"
echo ========================================================
echo Starting DocuAI Platform Frontend (Vite + React)...
echo Working Directory: %CD%
echo URL: http://localhost:5173
echo ========================================================
npm run dev -- --host
pause
