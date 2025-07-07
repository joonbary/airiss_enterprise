@echo off
echo ==========================================
echo Step 3: Deploy AIRISS Application
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Deploying application...
eb deploy

echo Checking deployment status...
eb status

echo Opening in browser...
eb open

echo ==========================================
echo Deployment completed successfully!
echo ==========================================
pause
