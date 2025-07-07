@echo off
echo ==========================================
echo AIRISS Final Deploy to Correct Environment
echo ==========================================

echo Step 1: Set airiss-prod as default environment...
eb use airiss-prod

echo Step 2: Deploy latest application...
eb deploy

echo Step 3: Check status...
eb status

echo Step 4: Open in browser...
eb open

echo ==========================================
echo AIRISS is now live on AWS!
echo URL: airiss-prod.eba-aaicpsr3.ap-northeast-2.elasticbeanstalk.com
echo ==========================================
pause
