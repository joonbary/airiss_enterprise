@echo off
echo ==========================================
echo AIRISS Phase 1.5 Enhanced Deployment
echo ==========================================

echo Step 1: Creating backup...
copy application.py application_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py

echo Step 2: Deploying enhanced version...
copy application_enhanced.py application.py

echo Step 3: Testing deployment...
eb deploy

echo Step 4: Waiting for deployment...
timeout 30

echo Step 5: Checking status...
eb status

echo Step 6: Testing health endpoint...
curl -f https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/health

if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Enhanced deployment completed!
    echo Executive Dashboard: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/executive
    echo Main Interface: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/
) else (
    echo WARNING: Health check failed
    echo Please check deployment logs with: eb logs --all
)

echo ==========================================
echo Deployment process finished
echo ==========================================
pause
