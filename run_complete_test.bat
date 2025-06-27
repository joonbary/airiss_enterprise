@echo off
echo ============================================================================
echo 🚀 AIRISS v4.0 완전 자동화 테스트 실행
echo ============================================================================
echo.

echo 📋 1단계: 서버 시작 확인
echo.

REM 포트 8002가 사용 중인지 확인
netstat -ano | findstr :8002 > nul
if %errorlevel% == 0 (
    echo ⚠️  포트 8002가 이미 사용 중입니다. 기존 서버를 종료하고 다시 시도하세요.
    echo 💡 해결방법: Ctrl+C로 기존 서버 종료 후 다시 실행
    pause
    exit /b 1
)

echo ✅ 포트 8002 사용 가능
echo.

echo 📋 2단계: AIRISS v4.0 서버 백그라운드 시작
start /b python -m app.main

echo ⏳ 서버 초기화 대기 중...
timeout /t 5 /nobreak > nul

echo.
echo 📋 3단계: 서버 상태 확인
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8002/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host '✅ 서버 정상 작동 확인'; exit 0 } else { Write-Host '❌ 서버 응답 오류'; exit 1 } } catch { Write-Host '❌ 서버 연결 실패'; exit 1 }"

if %errorlevel% neq 0 (
    echo.
    echo ❌ 서버 시작에 실패했습니다.
    echo 💡 수동으로 다음 명령어를 실행해보세요:
    echo    python -m app.main
    pause
    exit /b 1
)

echo.
echo 📋 4단계: 자동화 테스트 시작
echo.
python test_airiss_v4.py

echo.
echo 📋 5단계: 테스트 완료
echo.
echo 🌐 AIRISS v4.0 대시보드: http://localhost:8002/dashboard
echo 📚 API 문서: http://localhost:8002/docs
echo.
echo 서버를 종료하려면 Ctrl+C를 누르세요.
pause
