# start_enhanced_v4.bat
@echo off
echo ========================================
echo    AIRISS v4.0 Enhanced Server
echo    편향 탐지 + 예측 분석 통합 버전
echo ========================================
echo.

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    echo [1/3] 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else (
    echo [경고] 가상환경이 없습니다. 
    echo python -m venv venv 로 생성하세요.
)

REM 필요한 패키지 확인
echo.
echo [2/3] 필수 패키지 확인 중...
pip show scipy >nul 2>&1
if %errorlevel% neq 0 (
    echo scipy 설치 중...
    pip install scipy
)

pip show scikit-learn >nul 2>&1
if %errorlevel% neq 0 (
    echo scikit-learn 설치 중...
    pip install scikit-learn
)

pip show joblib >nul 2>&1
if %errorlevel% neq 0 (
    echo joblib 설치 중...
    pip install joblib
)

REM 서버 시작
echo.
echo [3/3] AIRISS v4.0 Enhanced 서버 시작 중...
echo.
echo ┌─────────────────────────────────────────────────┐
echo │  🚀 서버 시작 중...                             │
echo │  📊 Enhanced UI: http://localhost:8002/         │
echo │  📖 API 문서: http://localhost:8002/docs        │
echo │  🔍 편향 탐지: 활성화                           │
echo │  📈 예측 분석: 활성화                           │
echo └─────────────────────────────────────────────────┘
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8002 --reload

pause
