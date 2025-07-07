@echo off
chcp 65001 > nul
echo 🔍 AIRISS 프로젝트 빠른 상태 확인
echo =====================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📍 현재 브랜치:
git branch --show-current

echo.
echo 📊 Git 상태:
git status --porcelain

echo.
echo 🚀 마지막 커밋:
git log -1 --oneline

echo.
echo 🔧 활성 CI 파일:
if exist ".github\workflows\ci.yml" (
    echo ✅ ci.yml 존재
    findstr /i "name:" .github\workflows\ci.yml | head -1
) else (
    echo ❌ ci.yml 없음
)

echo.
echo 🌐 GitHub Actions 확인하려면 브라우저에서 열기:
echo https://github.com/joonbary/airiss_enterprise/actions
echo.

echo 📞 문제가 계속되면 ci_debug_fix.bat 실행하세요!
echo.
pause