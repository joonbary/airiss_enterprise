@echo off
echo ========================================
echo 🚀 AIRISS v4.0 수정 후 테스트 실행
echo ========================================
echo.

echo 📊 1. 서버 시작 (백그라운드)
start "AIRISS v4.0 Server" cmd /c "cd /d C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4 && python -m app.main"
echo    서버 시작 중... 5초 대기
timeout /t 5 /nobreak

echo.
echo 📋 2. 자동화 테스트 실행
python test_airiss_v4.py

echo.
echo ========================================
echo 🎯 테스트 완료!
echo ========================================
pause
