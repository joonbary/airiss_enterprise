@echo off
echo ========================================
echo  AIRISS v4.1 Enhanced 서버 시작
echo  Deep Learning Edition
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

REM Python 환경 활성화 (venv가 있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo [OK] 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] 가상환경이 없습니다. 전역 Python 사용
)

REM 필요한 패키지 확인
echo.
echo [*] 필요한 패키지 확인 중...
pip show fastapi uvicorn >nul 2>&1
if errorlevel 1 (
    echo [!] 필수 패키지 설치 중...
    pip install fastapi uvicorn websockets aiofiles pandas openpyxl
)

REM 서버 시작
echo.
echo ========================================
echo 🚀 AIRISS v4.1 Enhanced 서버를 시작합니다...
echo ========================================
echo.
echo 📍 접속 주소:
echo    - 메인 UI: http://localhost:8002/
echo    - API 문서: http://localhost:8002/docs
echo    - 대시보드: http://localhost:8002/dashboard
echo.
echo 💡 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

REM uvicorn으로 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload --log-level info

pause