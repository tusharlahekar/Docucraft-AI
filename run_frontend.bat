@echo off
cd /d "%~dp0\frontend"
echo ========================================================
echo Starting DocuAI Platform Frontend (Vite + React)...
echo ========================================================
npm run dev -- --host
pause
