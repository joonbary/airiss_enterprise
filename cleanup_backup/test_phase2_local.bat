@echo off
echo ========================================
echo AIRISS Phase 2 Core Services Test
echo ========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo [1/4] 가상환경 활성화...
call venv\Scripts\activate

echo.
echo [2/4] Phase 2 서버 시작...
echo 📡 서버 주소: http://localhost:8000
echo 🔧 상태 확인: http://localhost:8000/status
echo 🗄️ DB 상태: http://localhost:8000/health/db
echo 🧠 AI 상태: http://localhost:8000/health/analysis
echo.

echo [3/4] 로컬 테스트 실행 중...
python application_phase2_preparation.py

echo.
echo [4/4] 테스트 완료!
echo 브라우저에서 http://localhost:8000 접속하여 확인하세요.
echo.
pause
