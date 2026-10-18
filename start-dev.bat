@echo off
title Maccall Platform Launcher
echo ==========================================================
echo    MACCALL - LUXURY AI CREATOR MARKETPLACE ^& ATELIER     
echo ==========================================================
echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "Maccall Backend" cmd /k "cd backend && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite Frontend on port 5173...
start "Maccall Frontend" cmd /k "cd frontend && npx vite --port 5173 --host 127.0.0.1"

echo.
echo Services launched!
echo - Frontend: http://localhost:5173
echo - Backend: http://localhost:8000
echo - Swagger Docs: http://localhost:8000/docs
echo.
pause
