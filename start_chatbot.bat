@echo off
REM Start FastAPI Chatbot Server

echo Starting FastAPI Chatbot Server...
echo.

REM Navigate to chatbot directory
cd /d "%~dp0chatbot"

REM Install dependencies if needed
echo Checking dependencies...
pip install -q -r requirements.txt

REM Start uvicorn server with auto-reload
echo.
echo Starting server on http://localhost:8001
echo Press Ctrl+C to stop the server
echo.

uvicorn server:app --host 0.0.0.0 --port 8001 --reload

pause
