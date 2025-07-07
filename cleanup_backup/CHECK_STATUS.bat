@echo off
echo ==========================================
echo AIRISS Status Check
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Checking EB status...
eb status

echo Checking EB health...
eb health

echo ==========================================
echo Status check completed
echo ==========================================
pause
