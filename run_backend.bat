@echo off
echo ========================================================
echo Starting Enterprise DocuAI Assistant Backend (FastAPI)...
echo ========================================================
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
