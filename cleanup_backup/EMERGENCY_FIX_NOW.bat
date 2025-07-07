@echo off
echo =========================================
echo AIRISS AWS Emergency Recovery Script
echo =========================================
echo.

echo Step 1: Check current status...
eb status

echo.
echo Step 2: Health check...
eb health

echo.
echo Step 3: Get error logs...
eb logs --all > deployment_error_log.txt

echo.
echo Step 4: Emergency redeploy...
eb deploy

echo.
echo Step 5: Wait and check status...
timeout 30
eb status

echo.
echo =========================================
echo Recovery Complete! Check URL:
echo https://airiss-v4.ap-northeast-2.elasticbeanstalk.com
echo =========================================
pause
