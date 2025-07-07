@echo off
echo ==========================================
echo Step 2: Create EB Environment
echo ==========================================

cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4

echo Creating production environment...
eb create production --platform "Python 3.11 running on 64bit Amazon Linux 2023" --instance-type t3.micro --region ap-northeast-2

echo Environment creation completed!
eb status

echo ==========================================
echo Environment ready for deployment
echo ==========================================
pause
