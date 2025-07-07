@echo off
echo ================================
echo AIRISS Phase 1 Local Test
echo ================================

echo.
echo [1/3] Testing Python imports...
python -c "from fastapi import FastAPI; from fastapi.templating import Jinja2Templates; print('✅ All imports successful')"

if errorlevel 1 (
    echo ❌ Import test failed
    echo Installing missing dependencies...
    pip install -r requirements.txt
)

echo.
echo [2/3] Starting local server...
echo Press Ctrl+C to stop server
echo.
echo Test URLs:
echo - Main: http://localhost:8000/
echo - Status: http://localhost:8000/status
echo - Health: http://localhost:8000/health
echo.

python application.py

echo.
echo [3/3] Local test completed
pause
