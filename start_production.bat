@echo off
echo ========================================
echo   AIRISS v4.0 Production Build & Deploy
echo ========================================
echo.

set PROJECT_ROOT=%~dp0

echo 🏗️ React 앱 프로덕션 빌드 시작...
cd /d "%PROJECT_ROOT%airiss-v4-frontend"

REM npm 의존성 설치 확인
if not exist "node_modules" (
    echo 📦 npm install 실행 중...
    npm install
)

REM React 앱 빌드
echo 🔨 React 앱 빌드 중...
npm run build

if %ERRORLEVEL% EQU 0 (
    echo ✅ React 앱 빌드 완료!
) else (
    echo ❌ React 앱 빌드 실패!
    pause
    exit /b 1
)

echo.
echo 🚀 프로덕션 서버 시작...
cd /d "%PROJECT_ROOT%"

REM 환경 변수 설정
set ENVIRONMENT=production

REM 프로덕션 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

echo.
echo ========================================
echo   AIRISS v4.0 프로덕션 서버 실행 완료!
echo ========================================
echo 🌐 통합 앱: http://localhost:8002
echo 📖 API 문서: http://localhost:8002/docs
echo ========================================

pause