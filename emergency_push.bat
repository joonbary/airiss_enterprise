@echo off
REM ==========================================
REM AIRISS Emergency CI Fix - Git Push Script
REM ==========================================

echo AIRISS Emergency CI Fix Starting...
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Current directory: %CD%
echo.

echo Checking git status...
git status
echo.

echo Adding all changes...
git add .
echo.

echo Creating commit...
git commit -m "Emergency CI/CD Fix - Simplified pipeline for immediate deployment"

echo.
echo Pushing to GitHub...
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Changes pushed to GitHub!
    echo CI/CD pipeline should now pass
    echo Check: https://github.com/joonbary/airiss_enterprise/actions
) else (
    echo ERROR: Push failed. Check git configuration.
    echo Try: git remote -v
    echo Try: git branch -a
)

echo.
echo Next steps:
echo 1. Check GitHub Actions in 2 minutes
echo 2. Verify CI pipeline passes
echo 3. Resume deployment process
echo.

pause
