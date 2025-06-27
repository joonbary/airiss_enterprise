@echo off
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo ===========================================
echo   🚀 AIRISS v4.0 백엔드 서버 실행 테스트
echo ===========================================
echo.

echo 📍 현재 디렉토리: %cd%
echo.

echo 🔍 Python 가상환경 활성화 중...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 가상환경 활성화 완료
) else (
    echo ⚠️ 가상환경이 발견되지 않음. 전역 Python 사용
)
echo.

echo 🔧 Python 및 패키지 버전 확인...
python --version
pip list | findstr fastapi
pip list | findstr uvicorn
echo.

echo 🚀 AIRISS v4.0 서버 시작...
echo 📡 서버 주소: http://localhost:8002
echo 📖 API 문서: http://localhost:8002/docs  
echo 📊 대시보드: http://localhost:8002/dashboard
echo.
echo ⏰ 서버 시작 중... (Ctrl+C로 중지)
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

echo.
echo 🛑 서버가 종료되었습니다.
echo.
pause
