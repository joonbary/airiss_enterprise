@echo off
echo ==========================================
echo AIRISS EB Environment Setup and Deploy
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Step 1: Check current EB applications...
eb list

echo Step 2: Check if production environment exists...
eb status 2>nul || (
    echo Environment not found. Creating new environment...
    eb create production --platform "Python 3.11 running on 64bit Amazon Linux 2023" --instance-type t3.micro --region ap-northeast-2
)

echo Step 3: Deploy application...
eb deploy

echo Step 4: Check final status...
eb status

echo Step 5: Open in browser...
eb open

echo ==========================================
echo Setup and deployment completed!
echo ==========================================
pause
