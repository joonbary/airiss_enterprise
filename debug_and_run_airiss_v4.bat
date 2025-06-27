@echo off
echo ============================================================
echo AIRISS v4.0 디버깅 및 실행 스크립트
echo ============================================================
echo.

echo [1/5] 필수 패키지 설치...
echo.
echo scikit-learn 설치 중...
pip install scikit-learn >nul 2>&1 && echo ✅ scikit-learn 설치됨 || echo ❌ scikit-learn 설치 실패

echo scipy 설치 중...
pip install scipy >nul 2>&1 && echo ✅ scipy 설치됨 || echo ❌ scipy 설치 실패

echo aiohttp 설치 중...
pip install aiohttp >nul 2>&1 && echo ✅ aiohttp 설치됨 || echo ❌ aiohttp 설치 실패

echo.
echo [2/5] 서버 컴포넌트 테스트...
echo.
python test_server_components.py

echo.
echo [3/5] 서버 시작 준비...
echo.

REM 기존 프로세스 종료
echo 기존 서버 프로세스 확인 중...
tasklist /FI "WINDOWTITLE eq AIRISS v4.0*" 2>nul | find /I "python.exe" >nul && (
    echo 기존 서버 종료 중...
    taskkill /F /FI "WINDOWTITLE eq AIRISS v4.0*" >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo.
echo [4/5] AIRISS v4.0 서버 시작...
echo.
start "AIRISS v4.0 Enhanced Server" cmd /k "call venv\Scripts\activate && python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8002 --reload"

echo.
echo 서버 시작 대기 중...
timeout /t 5 /nobreak >nul

echo.
echo [5/5] 웹 브라우저 열기...
start http://localhost:8002/

echo.
echo ============================================================
echo AIRISS v4.0이 시작되었습니다!
echo.
echo - 메인 UI: http://localhost:8002/
echo - API 문서: http://localhost:8002/docs
echo - 대시보드: http://localhost:8002/dashboard
echo.
echo 서버 로그는 별도의 창에서 확인하세요.
echo.
echo 통합 테스트를 실행하려면 Enter를 누르세요...
pause >nul

echo.
echo 통합 테스트 실행 중...
python test_airiss_v4_integration.py

echo.
echo ============================================================
echo 모든 작업이 완료되었습니다!
echo ============================================================
pause
