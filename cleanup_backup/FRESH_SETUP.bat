@echo off
echo ==========================================
echo AIRISS Complete EB Setup from Scratch
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Step 1: Initialize EB application...
eb init --platform "Python 3.11 running on 64bit Amazon Linux 2023" --region ap-northeast-2

echo Step 2: Create production environment...
eb create production --instance-type t3.micro

echo Step 3: Deploy application...
eb deploy

echo Step 4: Check final status...
eb status

echo Step 5: Open in browser...
eb open

echo ==========================================
echo AIRISS is now live on AWS!
echo ==========================================
pause
