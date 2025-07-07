@echo off
echo =====================================
echo AIRISS Project Quick Status Check
echo =====================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Current branch:
git branch --show-current

echo.
echo Git status:
git status --porcelain

echo.
echo Last commit:
git log -1 --oneline

echo.
echo Active CI file:
if exist ".github\workflows\ci.yml" (
    echo CI file exists
    findstr /i "name:" .github\workflows\ci.yml
) else (
    echo CI file missing
)

echo.
echo To check GitHub Actions, open in browser:
echo https://github.com/joonbary/airiss_enterprise/actions
echo.

echo If problems persist, run: ci_debug_fix_safe.bat
echo.
pause