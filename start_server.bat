@echo off
REM AIRISS v4.0 서버 시작 스크립트
echo ===============================================
echo 🚀 AIRISS v4.0 서버 시작 중...
echo ===============================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📁 작업 디렉토리: %CD%
echo 📡 서버 포트: 8003
echo 🌐 대시보드: http://localhost:8003/dashboard
echo 📚 API 문서: http://localhost:8003/docs
echo.

echo 🔥 uvicorn 서버 시작...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

pause
