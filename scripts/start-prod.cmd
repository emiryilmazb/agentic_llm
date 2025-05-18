@echo off
echo Starting production environment...

REM Build frontend
cd frontend/chatbot-ui
call npm run build
cd ..\..

REM Start backend with production settings
cd backend
python run.py

echo Production server started!
echo Backend API: http://localhost:8000
