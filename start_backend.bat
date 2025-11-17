@echo off
echo Starting AI Claims Triage Backend Server...
cd /d "%~dp0"
echo.
echo Backend will start on http://localhost:8000
echo API Docs available at http://localhost:8000/docs
echo.
venv\Scripts\python.exe -m uvicorn fastapi_server:app --host 0.0.0.0 --port 8000 --reload
