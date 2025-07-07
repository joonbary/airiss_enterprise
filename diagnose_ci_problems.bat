@echo off
echo ========================================
echo AIRISS CI Problem Diagnosis Script
echo ========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Check specific CI failure reasons
echo ----------------------------------------

echo Checking frontend structure:
if exist "airiss-v4-frontend\package.json" (
    echo Frontend folder exists
    type airiss-v4-frontend\package.json | findstr "scripts"
) else (
    echo ERROR: Frontend folder missing
)

echo.
echo Checking backend requirements:
if exist "requirements.txt" (
    echo Requirements file exists
    echo First 10 dependencies:
    head -10 requirements.txt
) else (
    echo ERROR: Requirements file missing
)

echo.
echo Checking Docker setup:
if exist "Dockerfile" (
    echo Docker file exists
    head -5 Dockerfile
) else (
    echo ERROR: Dockerfile missing
)

echo.
echo Checking test files:
if exist "tests\" (
    echo Tests folder exists
    dir tests\
) else (
    echo ERROR: Tests folder missing
)

echo.
echo ========================================
echo DIAGNOSIS COMPLETE
echo ========================================
echo.
echo Based on the results above, we can fix CI properly
echo instead of disabling it completely.
echo.
pause