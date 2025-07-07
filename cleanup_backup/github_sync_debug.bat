@echo off
chcp 65001 > nul
echo 🚀 AIRISS GitHub 동기화 도구 (디버그 모드)
echo ================================
echo.

echo 🔍 환경 확인 중...
echo.

REM 현재 경로 확인
echo 📁 현재 경로: %CD%
echo.

REM Python 설치 확인
echo 🐍 Python 설치 상태 확인:
python --version
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다.
    echo.
    echo 🔧 해결 방법:
    echo 1. Python이 설치되어 있다면 환경변수 PATH 확인
    echo 2. 또는 아래 대안 방법 사용
    echo.
    pause
    goto alternatives
)

echo ✅ Python 정상 설치됨
echo.

REM 프로젝트 폴더로 이동
echo 📂 프로젝트 폴더로 이동:
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
if errorlevel 1 (
    echo ❌ 프로젝트 폴더를 찾을 수 없습니다.
    echo 📁 현재 경로: %CD%
    pause
    exit /b 1
)

echo ✅ 프로젝트 폴더 이동 완료: %CD%
echo.

REM 필요한 파일들 확인
echo 📋 필요한 파일 확인:
if exist "github_sync_checker.py" (
    echo ✅ github_sync_checker.py 존재
) else (
    echo ❌ github_sync_checker.py 없음
)

if exist "github_sync_updater.py" (
    echo ✅ github_sync_updater.py 존재
) else (
    echo ❌ github_sync_updater.py 없음
)

echo.

:menu
echo 📋 메뉴를 선택하세요:
echo.
echo 1. 현재 상태 진단하기
echo 2. GitHub에 안전하게 업데이트하기  
echo 3. GitHub 페이지 열기
echo 4. 프로젝트 폴더 열기
echo 5. 환경 정보 다시 확인
echo 6. 대안 방법 보기
echo 7. 종료
echo.

set /p choice="선택 (1-7): "

if "%choice%"=="1" (
    echo.
    echo 🔍 현재 상태를 진단합니다...
    python github_sync_checker.py
    if errorlevel 1 (
        echo ❌ 진단 스크립트 실행 실패
        echo 💡 대안 방법을 확인하세요 (메뉴 6)
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="2" (
    echo.
    echo 🔧 GitHub 업데이트를 진행합니다...
    python github_sync_updater.py
    if errorlevel 1 (
        echo ❌ 업데이트 스크립트 실행 실패
        echo 💡 대안 방법을 확인하세요 (메뉴 6)
    )
    echo.
    pause
    goto menu
)

if "%choice%"=="3" (
    echo.
    echo 🌐 GitHub 페이지를 엽니다...
    start https://github.com/joonbary/airiss_enterprise
    echo ✅ 브라우저에서 페이지가 열렸습니다.
    pause
    goto menu
)

if "%choice%"=="4" (
    echo.
    echo 📁 프로젝트 폴더를 엽니다...
    explorer "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    echo ✅ 파일 탐색기가 열렸습니다.
    pause
    goto menu
)

if "%choice%"=="5" (
    echo.
    echo 🔍 환경 정보를 다시 확인합니다...
    echo 📁 현재 경로: %CD%
    echo 🐍 Python 버전:
    python --version
    echo 💻 시스템 정보:
    echo    OS: %OS%
    echo    사용자: %USERNAME%
    echo    컴퓨터: %COMPUTERNAME%
    echo.
    pause
    goto menu
)

if "%choice%"=="6" (
    goto alternatives
)

if "%choice%"=="7" (
    echo.
    echo 👋 안녕히 가세요!
    pause
    exit /b 0
)

echo ❌ 잘못된 선택입니다. 다시 시도하세요.
pause
goto menu

:alternatives
cls
echo 🔧 대안 방법 (Python 문제 시)
echo ================================
echo.
echo 다음 방법들을 시도해보세요:
echo.
echo 📌 방법 1: 명령 프롬프트 직접 사용
echo    1. Win + R 키 누르기
echo    2. "cmd" 입력하고 엔터
echo    3. 다음 명령어 복사해서 붙여넣기:
echo       cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
echo       python github_sync_checker.py
echo.
echo 📌 방법 2: 파일 탐색기에서 실행
echo    1. C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4 폴더 열기
echo    2. github_sync_checker.py 파일 우클릭
echo    3. "연결 프로그램" → "Python" 선택
echo.
echo 📌 방법 3: Git Bash 사용 (Git 설치된 경우)
echo    1. 프로젝트 폴더에서 우클릭
echo    2. "Git Bash Here" 선택
echo    3. python github_sync_checker.py 입력
echo.
echo 📌 방법 4: 수동 Git 명령어
echo    1. Git Bash 또는 명령 프롬프트에서:
echo       git status
echo       git add .
echo       git commit -m "Update to v4.1"
echo       git push origin main
echo.
pause

set /p back="메인 메뉴로 돌아가시겠습니까? (y/N): "
if /i "%back%"=="y" goto menu

echo 👋 문제 해결을 위해 개발팀에 문의하세요.
pause
exit /b 0
