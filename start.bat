@echo off
echo ================================================
echo Starting AI Claims Triage System
echo ================================================
echo.

echo Starting Backend Server (FastAPI)...
start "Backend Server" cmd /k "python fastapi_server.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend Server (React)...
start "Frontend Server" cmd /k "cd frontend-react && npm start"

echo.
echo ================================================
echo Servers starting...
echo ================================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ================================================
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Frontend Server*" /T /F >nul 2>&1
echo Servers stopped.
