@echo off
echo ========================================
echo  AIRISS v4.1 서버 재시작 스크립트
echo ========================================
echo.

echo 🔍 실행 중인 Python 프로세스 확인...
tasklist | findstr python

echo.
echo ⚠️  기존 Python 프로세스를 종료합니다...
taskkill /IM python.exe /F 2>nul

echo.
echo ⏳ 포트 해제를 위해 5초 대기...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 AIRISS v4.1 서버를 시작합니다...
echo.

:: 기본 포트로 시작 시도
python run_server.py

:: 만약 실패하면 대체 포트로 시작
if errorlevel 1 (
    echo.
    echo ⚠️  포트 8002 사용 불가. 포트 8003으로 재시도...
    python run_server_alt.py --port 8003
)

pause
