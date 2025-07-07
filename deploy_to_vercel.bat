@echo off
echo 🚀 AIRISS V4 Vercel 배포 자동화 스크립트
echo ==========================================

REM 현재 디렉토리 확인
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend"
echo 📍 현재 위치: %CD%

REM 1단계: 빌드 테스트
echo.
echo 🔨 1단계: 빌드 테스트 중...
call npm run build
if errorlevel 1 (
    echo ❌ 빌드 실패! 오류를 확인하고 다시 시도하세요.
    pause
    exit /b 1
)
echo ✅ 빌드 성공!

REM 2단계: 배포용 디렉토리 생성
echo.
echo 📁 2단계: 배포용 프로젝트 준비 중...
set DEPLOY_DIR=%USERPROFILE%\Desktop\airiss-frontend-deploy
if exist "%DEPLOY_DIR%" (
    echo 🗑️ 기존 배포 폴더 삭제 중...
    rmdir /s /q "%DEPLOY_DIR%"
)
mkdir "%DEPLOY_DIR%"

REM 3단계: 파일 복사
echo 📋 3단계: 필요한 파일들 복사 중...
xcopy "src" "%DEPLOY_DIR%\src\" /E /I /H /Y
xcopy "public" "%DEPLOY_DIR%\public\" /E /I /H /Y
xcopy "package.json" "%DEPLOY_DIR%\" /Y
xcopy "tsconfig.json" "%DEPLOY_DIR%\" /Y
xcopy ".env.production" "%DEPLOY_DIR%\" /Y
xcopy "vercel.json" "%DEPLOY_DIR%\" /Y
if exist "README.md" xcopy "README.md" "%DEPLOY_DIR%\" /Y

REM 불필요한 파일 제외
if exist "%DEPLOY_DIR%\.env" del "%DEPLOY_DIR%\.env"

cd /d "%DEPLOY_DIR%"

REM 4단계: package.json 최적화
echo ⚙️ 4단계: package.json 최적화 중...
powershell -Command "(Get-Content package.json) | ForEach-Object { $_ -replace '\"private\": true,', '\"private\": false, \"homepage\": \".\",'; } | Set-Content package.json"

REM 5단계: 의존성 설치
echo 📦 5단계: 의존성 설치 중...
call npm install --production=false

REM 6단계: 최종 빌드 테스트
echo 🔍 6단계: 최종 빌드 테스트 중...
call npm run build
if errorlevel 1 (
    echo ❌ 최종 빌드 실패!
    pause
    exit /b 1
)

REM 7단계: Git 초기화
echo 🐙 7단계: Git 저장소 초기화 중...
git init
git add .
git commit -m "🚀 AIRISS V4 Frontend - Ready for Vercel Deployment"

echo.
echo ✅ 모든 준비가 완료되었습니다!
echo.
echo 📍 배포용 파일 위치: %DEPLOY_DIR%
echo.
echo 🎯 다음 단계:
echo 1. GitHub에서 새 저장소 생성: airiss-v4-frontend
echo 2. 다음 명령어 실행:
echo    git branch -M main
echo    git remote add origin https://github.com/[YOUR-USERNAME]/airiss-v4-frontend.git
echo    git push -u origin main
echo.
echo 3. vercel.com에서 GitHub 저장소 연결하여 배포
echo.
echo 🌐 배포 후 접속 테스트:
echo    - 메인 페이지 로딩 확인
echo    - 라우팅 동작 확인 (/dashboard, /upload 등)
echo    - 콘솔 에러 없음 확인
echo.
pause
