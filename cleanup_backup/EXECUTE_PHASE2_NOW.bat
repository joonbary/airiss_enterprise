@echo off
echo ================================================
echo 🚀 AIRISS Phase 2 Core 실행 중...
echo ================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📂 현재 디렉토리: %CD%
echo.

echo 🧠 Python 환경 확인...
python --version
echo.

echo 🔧 필수 모듈 확인...
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import pandas; print('✅ Pandas OK')"
python -c "import sqlite3; print('✅ SQLite OK')"
echo.

echo 🚀 Phase 2 Core 서버 시작...
echo 📡 서버 주소: http://localhost:8000
echo 📊 상태 확인: http://localhost:8000/status  
echo 🏥 헬스체크: http://localhost:8000/health
echo.
echo ⚠️ 서버를 중지하려면 Ctrl+C를 누르세요
echo.

python application_phase2_preparation.py

pause
