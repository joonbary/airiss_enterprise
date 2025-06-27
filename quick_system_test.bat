@echo off
chcp 65001
echo ========================================
echo   AIRISS v4.0 Quick System Test
echo ========================================
echo.

echo Testing Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Testing Node.js installation...
node --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

echo.
echo Testing npm installation...
npm --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)

echo.
echo Checking project structure...
if not exist "app" (
    echo ERROR: app directory not found!
    pause
    exit /b 1
)

if not exist "airiss-v4-frontend" (
    echo ERROR: airiss-v4-frontend directory not found!
    pause
    exit /b 1
)

echo.
echo Running integration test...
python test_integration.py

echo.
echo ========================================
echo   System Test Complete
echo ========================================
pause