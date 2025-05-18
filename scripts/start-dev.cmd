@echo off
echo Starting development environment...

REM Start backend in a new command window
start cmd /k "cd backend && python run.py"

REM Wait a moment to ensure backend starts first
timeout /t 3

REM Start frontend in another command window
start cmd /k "cd frontend/chatbot-ui && npm start"

echo Development servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
