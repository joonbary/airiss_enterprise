@echo off
echo ========================================
echo AIRISS v4.1 서버 재시작 스크립트
echo ========================================
echo.

echo [1] 기존 서버 프로세스 종료 중...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq AIRISS*" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq run_server.py*" 2>nul
timeout /t 2 /nobreak > nul

echo [2] 포트 8002 점유 프로세스 확인 및 종료...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8002') do (
    echo 포트 8002를 사용 중인 프로세스 종료: PID %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak > nul

echo [3] 브라우저 캐시 클리어 권장
echo    - Chrome: Ctrl + Shift + Del
echo    - 또는 개발자 도구에서 "Empty Cache and Hard Reload"
echo.

echo [4] 서버 재시작 중...
cd /d "%~dp0"
start "AIRISS v4.1 Enhanced Server" python run_server.py

echo.
echo ✅ 서버가 재시작되었습니다!
echo    http://localhost:8002/ 에서 확인하세요.
echo.
echo ========================================
pause
