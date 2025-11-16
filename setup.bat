@echo off
echo ================================================
echo AI Claims Triage - Enhanced Setup
echo ================================================
echo.

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing Python dependencies
    pause
    exit /b 1
)
echo ✓ Python dependencies installed
echo.

echo [2/4] Initializing enhanced database...
cd src\api
python init_enhanced_db.py
if %ERRORLEVEL% NEQ 0 (
    echo Error initializing database
    pause
    exit /b 1
)
cd ..\..
echo ✓ Database initialized
echo.

echo [3/4] Installing frontend dependencies...
cd frontend-react
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo Error installing frontend dependencies
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend dependencies installed
echo.

echo [4/4] Setup complete!
echo.
echo ================================================
echo Next steps:
echo ================================================
echo 1. Start backend:  python fastapi_server.py
echo 2. Start frontend: cd frontend-react ^&^& npm start
echo 3. Open browser:   http://localhost:3000
echo.
echo Demo accounts:
echo - Customer: customer@demo.com / password123
echo - Admin:    admin@demo.com / admin123
echo ================================================
echo.
pause
