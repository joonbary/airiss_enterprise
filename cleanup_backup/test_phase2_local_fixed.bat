@echo off
chcp 65001 >nul
echo ========================================
echo AIRISS Phase 2 Core Services Test
echo ========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo [1/4] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
    echo Virtual environment activated
) else (
    echo WARNING: Virtual environment not found
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
)

echo.
echo [2/4] Starting Phase 2 server...
echo Server URL: http://localhost:8000
echo Status Check: http://localhost:8000/status
echo DB Health: http://localhost:8000/health/db
echo AI Health: http://localhost:8000/health/analysis
echo.

echo [3/4] Running local test...
python application_phase2_preparation.py

echo.
echo [4/4] Test completed!
echo Open browser and go to http://localhost:8000
echo.
pause
