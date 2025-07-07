@echo off
echo ================================
echo AIRISS Phase 1 UI Recovery Deploy
echo ================================

echo.
echo [1/5] Creating deployment backup...
copy application.py application_phase1_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py

echo.
echo [2/5] Checking current AWS status...
call eb health --refresh

echo.
echo [3/5] Deploying Phase 1 version...
call eb deploy

echo.
echo [4/5] Waiting for deployment...
timeout /t 30

echo.
echo [5/5] Checking deployment status...
call eb health --refresh
call eb status

echo.
echo ================================
echo Phase 1 Deployment Complete!
echo ================================
echo.
echo Testing URLs:
echo - Main: http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/
echo - Status: http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/status  
echo - Health: http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/health
echo.
echo Next: Phase 2 (Core Functions) deployment tomorrow morning
echo.
pause
