@echo off
echo ==========================================
echo AIRISS Health Check Diagnosis
echo ==========================================

echo Step 1: Check detailed health status...
eb health --refresh

echo Step 2: Get recent logs...
eb logs --all

echo Step 3: Check environment events...
eb events

echo Step 4: Check if URL is accessible...
curl -I https://airiss-prod.eba-aaicpsr3.ap-northeast-2.elasticbeanstalk.com

echo Step 5: Check health endpoint...
curl -I https://airiss-prod.eba-aaicpsr3.ap-northeast-2.elasticbeanstalk.com/health

echo ==========================================
echo Diagnosis Complete
echo ==========================================
pause
