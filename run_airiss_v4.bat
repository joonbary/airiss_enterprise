@echo off
echo ========================================
echo  AIRISS v4.1 Enhanced 서버 시작
echo ========================================
echo.

:: Python 환경 활성화 (venv가 있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

:: 필요한 패키지 설치 확인
echo 필요한 패키지 확인 중...
pip install -r requirements.txt >nul 2>&1

:: 서버 시작
echo.
echo AIRISS v4.1 Enhanced 서버를 시작합니다...
echo.
echo 접속 주소:
echo - 메인 UI: http://localhost:8002/
echo - API 문서: http://localhost:8002/docs
echo - 대시보드: http://localhost:8002/dashboard
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo ========================================
echo.

:: Python 모듈로 실행 (올바른 경로 설정)
python -m app.main

pause
