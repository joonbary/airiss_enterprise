@echo off
echo ========================================
echo   AIRISS v4.0 Enhanced UI/UX 시작
echo ========================================
echo.

cd /d "%~dp0"

echo 📍 현재 디렉토리: %CD%
echo.

echo 🔍 Python 환경 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다.
    echo 💡 Python 3.8 이상을 설치하고 PATH를 설정해주세요.
    pause
    exit /b 1
)

python --version
echo.

echo 🔍 필수 패키지 확인 중...
python -c "import fastapi, uvicorn, sqlite3" >nul 2>&1
if errorlevel 1 (
    echo ❌ 필수 패키지가 누락되었습니다.
    echo 💡 requirements.txt 파일로 패키지를 설치해주세요:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ 필수 패키지 확인 완료
echo.

echo 🚀 AIRISS v4.0 Enhanced UI/UX 서버 시작 중...
echo.
echo 🌐 접속 정보:
echo    메인 UI (Enhanced): http://localhost:8002/
echo    개발자 대시보드:    http://localhost:8002/dashboard  
echo    API 문서:          http://localhost:8002/docs
echo.
echo 💡 서버를 중지하려면 Ctrl+C를 누르세요
echo ========================================
echo.

python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8002 --reload

echo.
echo ========================================
echo   AIRISS v4.0 Enhanced 서버 종료됨
echo ========================================
pause
