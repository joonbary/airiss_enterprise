@echo off
echo ========================================
echo   AIRISS v4.0 Development Environment
echo ========================================
echo.

REM Save current directory
set CURRENT_DIR=%cd%
set PROJECT_ROOT=%~dp0

echo Starting AIRISS v4.0 React Integration Development Environment
echo Project Root: %PROJECT_ROOT%
echo.

REM Start Backend Server (Background)
echo Starting Backend Server...
start "AIRISS Backend" cmd /k "cd /d %PROJECT_ROOT% && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"

REM Wait 3 seconds
timeout /t 3

REM Start React Development Server
echo Starting React Development Server...
cd /d "%PROJECT_ROOT%airiss-v4-frontend"

REM Check npm installation
if not exist "node_modules" (
    echo Node modules not found. Running npm install...
    npm install
)

REM Start React development server
echo Starting React App...
npm start

echo.
echo ========================================
echo   AIRISS v4.0 Development Environment Ready!
echo ========================================
echo React App: http://localhost:3000
echo Backend API: http://localhost:8002
echo API Documentation: http://localhost:8002/docs
echo Development Dashboard: http://localhost:8002/dashboard
echo ========================================

pause