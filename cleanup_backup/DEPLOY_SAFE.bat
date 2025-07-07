@echo off
echo ==========================================
echo AIRISS AWS Deploy - Safe Mode
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Step 1: Deploy to AWS...
eb deploy

echo Step 2: Check deployment status...
eb status

echo Step 3: Open in browser...
eb open

echo ==========================================
echo Deployment completed! Check browser.
echo ==========================================
pause
