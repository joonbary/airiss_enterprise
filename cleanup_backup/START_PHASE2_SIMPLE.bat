@echo off
echo AIRISS Phase 2 Core Services Test
echo ====================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo [1/3] Activating virtual environment...
call venv\Scripts\activate

echo.
echo [2/3] Starting Phase 2 server...
echo Server: http://localhost:8000
echo Status: http://localhost:8000/status
echo.

python application_phase2_preparation.py

echo.
echo [3/3] Test completed!
pause
