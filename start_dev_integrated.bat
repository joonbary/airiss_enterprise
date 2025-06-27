@echo off
echo ========================================
echo   AIRISS v4.0 React Integration Setup
echo ========================================
echo.

REM 현재 디렉토리 저장
set CURRENT_DIR=%cd%
set PROJECT_ROOT=%~dp0

echo 🚀 AIRISS v4.0 React 통합 개발 환경 시작
echo 📁 프로젝트 루트: %PROJECT_ROOT%
echo.

REM 백엔드 서버 실행 (백그라운드)
echo 🔧 백엔드 서버 시작 중...
start "AIRISS Backend" cmd /k "cd /d %PROJECT_ROOT% && python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload"

REM 3초 대기
timeout /t 3

REM React 개발 서버 실행
echo 🌐 React 개발 서버 시작 중...
cd /d "%PROJECT_ROOT%airiss-v4-frontend"

REM npm 설치 확인
if not exist "node_modules" (
    echo 📦 Node modules가 없습니다. npm install을 실행합니다...
    npm install
)

REM React 개발 서버 시작
echo 🚀 React 앱 시작...
npm start

echo.
echo ========================================
echo   AIRISS v4.0 개발 환경이 실행되었습니다!
echo ========================================
echo 🌐 React 앱: http://localhost:3000
echo 🔧 백엔드 API: http://localhost:8002
echo 📖 API 문서: http://localhost:8002/docs
echo 📊 개발 대시보드: http://localhost:8002/dashboard
echo ========================================

pause