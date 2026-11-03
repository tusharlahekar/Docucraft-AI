@echo off
echo ========================================================
echo Launching Enterprise AI Chatbot & Document Generation Platform
echo 100%% Free & Open Source (Zero Paid APIs)
echo ========================================================
start "DocuAI Backend (FastAPI)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "DocuAI Frontend (React + Vite)" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
echo Platform successfully launched!
echo - Frontend: http://localhost:5173
echo - Backend API Docs: http://localhost:8000/docs
echo.
pause
