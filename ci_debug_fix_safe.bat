@echo off
echo ========================================
echo AIRISS CI/CD Debug and Fix Script
echo ========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Step 1: Check current Git status
echo ----------------------------------------
git status
git branch -a
echo.
echo Recent 5 commits:
git log --oneline -5

echo.
echo Step 2: Switch to main branch
echo ----------------------------------------
git checkout main
git pull origin main

echo.
echo Step 3: Check CI configuration
echo ----------------------------------------
echo Current CI files:
dir .github\workflows\*.yml

echo.
echo Current active CI content:
type .github\workflows\ci.yml

echo.
echo Step 4: GitHub Actions link
echo ----------------------------------------
echo Check GitHub Actions in browser:
echo https://github.com/joonbary/airiss_enterprise/actions
echo.

echo Step 5: Replace with emergency CI if needed
echo ----------------------------------------
echo If current CI keeps failing, replace with emergency CI? 
set /p choice="Y/N: "

if /i "%choice%"=="Y" (
    echo Replacing with emergency CI...
    copy .github\workflows\ci.yml .github\workflows\ci_current_backup.yml
    copy .github\workflows\emergency_ci.yml .github\workflows\ci.yml
    echo Emergency CI replacement completed
) else (
    echo Keeping current CI configuration
)

echo.
echo Step 6: Push changes to GitHub
echo ----------------------------------------
git add .
git commit -m "Fix: CI/CD pipeline debugging and emergency fix"
git push origin main

echo.
echo Completed! Check GitHub Actions in 2-3 minutes.
echo GitHub Actions: https://github.com/joonbary/airiss_enterprise/actions
echo.
pause