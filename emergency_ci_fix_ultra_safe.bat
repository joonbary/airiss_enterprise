@echo off
rem AIRISS Emergency CI Fix - Ultra Safe Version
rem No encoding issues, pure ASCII

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Current Git Status:
git status

echo.
echo Switching to main branch:
git checkout main
git pull origin main

echo.
echo Checking CI files:
dir .github\workflows

echo.
echo Replacing CI with emergency version:
copy .github\workflows\emergency_ci.yml .github\workflows\ci.yml

echo.
echo Committing changes:
git add .
git commit -m "Emergency CI fix - ultra safe version"
git push origin main

echo.
echo Done. Check: https://github.com/joonbary/airiss_enterprise/actions
pause