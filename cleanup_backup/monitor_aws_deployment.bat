@echo off
echo ========================================
echo 📊 AIRISS v4 실시간 AWS 모니터링
echo ========================================

:MONITOR_LOOP
echo.
echo ⏰ %date% %time%
echo ----------------------------------------

echo 🔍 1. 환경 상태 확인...
eb health --verbose

echo.
echo 🔍 2. 애플리케이션 상태...
eb status

echo.
echo 🔍 3. 최신 로그 (마지막 50줄)...
eb logs --all | tail -50

echo.
echo 🔍 4. HTTP 헬스체크 시도...
for /f "tokens=2 delims= " %%a in ('eb status ^| findstr "CNAME"') do set APP_URL=%%a
if defined APP_URL (
    echo 📡 URL: http://%APP_URL%/health
    curl -s -o nul -w "HTTP Status: %%{http_code} - Response Time: %%{time_total}s\n" http://%APP_URL%/health
    curl -s -o nul -w "Root Status: %%{http_code} - Response Time: %%{time_total}s\n" http://%APP_URL%/
) else (
    echo ❌ URL을 찾을 수 없습니다
)

echo.
echo ----------------------------------------
echo 📊 30초 후 다시 확인... (Ctrl+C로 중단)
timeout /t 30 /nobreak >nul

goto MONITOR_LOOP