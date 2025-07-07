@echo off
echo ==========================================
echo AIRISS Environment Fix and Deploy
echo ==========================================

echo Step 1: List all environments...
eb list

echo Step 2: Use existing production environment...
eb use production

echo Step 3: Deploy application...
eb deploy

echo Step 4: Check status...
eb status

echo Step 5: Open in browser...
eb open

echo ==========================================
echo AIRISS is now live on AWS!
echo ==========================================
pause
