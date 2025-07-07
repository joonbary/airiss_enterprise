@echo off
echo ==========================================
echo Step 1: Check EB Status
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Checking EB applications...
eb list

echo Checking current environment...
eb status

echo ==========================================
echo Status check completed
echo ==========================================
pause
