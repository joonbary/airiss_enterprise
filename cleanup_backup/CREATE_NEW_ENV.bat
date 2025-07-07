@echo off
echo ==========================================
echo AIRISS New Environment Creation
echo ==========================================

echo Step 1: Create new environment with different name...
eb create airiss-prod --instance-type t3.micro

echo Step 2: Deploy application...
eb deploy

echo Step 3: Check status...
eb status

echo Step 4: Open in browser...
eb open

echo ==========================================
echo AIRISS is now live on AWS!
echo ==========================================
pause
