# AIRISS Phase 2 - Quick Start Guide
# Simple manual commands for testing

## Option 1: Direct Python (Simplest)
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python application_phase2_preparation.py

## Option 2: With Virtual Environment
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
venv\Scripts\activate
python application_phase2_preparation.py

## Option 3: Install dependencies first
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
venv\Scripts\activate
pip install fastapi uvicorn jinja2 python-multipart
python application_phase2_preparation.py

## Option 4: PowerShell (UTF-8 safe)
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
powershell -ExecutionPolicy Bypass -File test_phase2_local.ps1

## Option 5: Fixed Batch File (English only)
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
test_phase2_local_fixed.bat

## Expected Output:
Server URL: http://localhost:8000
Status: http://localhost:8000/status
DB Health: http://localhost:8000/health/db
AI Health: http://localhost:8000/health/analysis

## Troubleshooting:
If you get import errors:
- pip install fastapi uvicorn jinja2 python-multipart

If you get encoding errors:
- Use Option 4 (PowerShell) or Option 1 (Direct Python)

If you get port errors:
- Change PORT in application_phase2_preparation.py from 8000 to 8001
