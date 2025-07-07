@echo off
echo ==========================================
echo AIRISS Quick Health Fix
echo ==========================================

echo Step 1: Restart environment...
eb restart

echo Step 2: Wait for restart...
timeout 60

echo Step 3: Check status...
eb status

echo Step 4: Check health...
eb health

echo ==========================================
echo Health Check Complete
echo ==========================================
pause
