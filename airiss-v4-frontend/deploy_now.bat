@echo off
echo 🎉 현재 위치에서 배포 패키지 생성 시작!
echo ================================================

REM 현재 위치 확인
echo 📍 현재 위치: %CD%

REM 배포용 폴더 생성
set DEPLOY_DIR=%USERPROFILE%\Desktop\airiss-frontend-deploy
echo 📁 배포용 폴더: %DEPLOY_DIR%

if exist "%DEPLOY_DIR%" (
    echo 🗑️ 기존 배포 폴더 삭제 중...
    rmdir /s /q "%DEPLOY_DIR%"
)
mkdir "%DEPLOY_DIR%"

echo 📋 파일 복사 중...
xcopy "src" "%DEPLOY_DIR%\src\" /E /I /H /Y
xcopy "public" "%DEPLOY_DIR%\public\" /E /I /H /Y
xcopy "package.json" "%DEPLOY_DIR%\" /Y
xcopy "tsconfig.json" "%DEPLOY_DIR%\" /Y
xcopy ".env.production" "%DEPLOY_DIR%\" /Y
xcopy "vercel.json" "%DEPLOY_DIR%\" /Y

REM theme 폴더가 있다면 복사
if exist "theme" xcopy "theme" "%DEPLOY_DIR%\theme\" /E /I /H /Y

REM README.md가 있다면 복사
if exist "README.md" xcopy "README.md" "%DEPLOY_DIR%\" /Y

REM 개발용 .env 파일 제거
if exist "%DEPLOY_DIR%\.env" del "%DEPLOY_DIR%\.env"

REM 배포 폴더로 이동
cd /d "%DEPLOY_DIR%"

echo ⚙️ package.json 최적화 중...
powershell -Command "(Get-Content package.json) -replace '\"private\": true,', '\"private\": false,\"homepage\": \".\",'; | Set-Content package.json"

echo 📦 의존성 설치 중...
call npm install

echo 🔍 최종 빌드 테스트 중...
call npm run build
if errorlevel 1 (
    echo ❌ 최종 빌드 실패!
    pause
    exit /b 1
)

echo 🐙 Git 저장소 초기화 중...
git init
git add .
git commit -m "🚀 AIRISS V4 Frontend - Ready for Vercel Deployment"

echo.
echo ✅ 배포 패키지 생성 완료!
echo.
echo 📍 배포용 파일 위치: %DEPLOY_DIR%
echo.
echo 🎯 GitHub 저장소 생성 후 다음 명령어 실행:
echo    git branch -M main
echo    git remote add origin https://github.com/[YOUR-USERNAME]/airiss-v4-frontend.git
echo    git push -u origin main
echo.
echo 🌐 Vercel 배포:
echo    1. vercel.com 접속
echo    2. Continue with GitHub
echo    3. New Project 클릭
echo    4. airiss-v4-frontend 저장소 선택
echo    5. Deploy 클릭
echo.
pause
