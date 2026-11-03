@echo off
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
echo ========================================================
echo Launching Enterprise AI Chatbot & Document Generation Platform
echo 100%% Free & Open Source (Zero Paid APIs)
echo ========================================================
echo Starting Backend Server in new window...
start "DocuAI Backend (FastAPI)" cmd /c "run_backend.bat"
timeout /t 3 /nobreak >nul
echo Starting Frontend Server in new window...
start "DocuAI Frontend (React + Vite)" cmd /c "run_frontend.bat"
timeout /t 3 /nobreak >nul
echo Opening Browser to http://localhost:5173...
start http://localhost:5173
echo.
echo Platform successfully launched!
echo - Frontend: http://localhost:5173
echo - Backend API Docs: http://localhost:8000/docs
echo.
pause
