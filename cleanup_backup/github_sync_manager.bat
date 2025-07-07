@echo off
chcp 65001 > nul
echo 🚀 AIRISS GitHub 동기화 도구
echo ================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 메뉴를 선택하세요:
echo.
echo 1. 현재 상태 진단하기 (권장)
echo 2. GitHub에 안전하게 업데이트하기
echo 3. GitHub 페이지 열기
echo 4. 프로젝트 폴더 열기
echo 5. 종료
echo.

set /p choice="선택 (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🔍 현재 상태를 진단합니다...
    python github_sync_checker.py
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 🔧 GitHub 업데이트를 진행합니다...
    python github_sync_updater.py
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo 🌐 GitHub 페이지를 엽니다...
    start https://github.com/joonbary/airiss_enterprise
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo 📁 프로젝트 폴더를 엽니다...
    explorer "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo 👋 안녕히 가세요!
    exit /b 0
)

echo ❌ 잘못된 선택입니다. 다시 시도하세요.
pause

:menu
cls
echo 🚀 AIRISS GitHub 동기화 도구
echo ================================
echo.
goto choice
