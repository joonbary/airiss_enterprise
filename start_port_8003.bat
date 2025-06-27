@echo off
echo ========================================
echo  AIRISS v4.1 - 대체 포트 실행 (8003)
echo ========================================
echo.

:: 포트 충돌 해결을 위해 8003 포트 사용
echo 🔍 포트 8002가 사용 중이므로 8003 포트를 사용합니다.
echo.

:: Python 환경 확인
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    pause
    exit /b 1
)

:: 필요한 패키지 확인
echo 📦 필요한 패키지 확인 중...
pip install fastapi uvicorn websockets sqlalchemy pandas openpyxl python-multipart >nul 2>&1

:: 서버 시작
echo.
echo 🚀 AIRISS v4.1 서버를 포트 8003에서 시작합니다...
echo.
echo ✨ 접속 주소:
echo   - 메인 페이지: http://localhost:8003/
echo   - API 문서: http://localhost:8003/docs
echo   - 대시보드: http://localhost:8003/dashboard
echo.
echo 💡 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

:: uvicorn으로 8003 포트에서 실행
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

pause
