@echo off
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
echo ========================================================
echo Starting Enterprise DocuAI Assistant Backend (FastAPI)...
echo Working Directory: %CD%
echo URL: http://localhost:8000
echo ========================================================
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
