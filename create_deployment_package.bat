@echo off
echo 🎉 빌드 성공! 이제 배포용 프로젝트를 생성합니다.
echo ================================================

REM 배포용 폴더 생성
set DEPLOY_DIR=%USERPROFILE%\Desktop\airiss-frontend-deploy
echo 📁 배포용 폴더 생성: %DEPLOY_DIR%

if exist "%DEPLOY_DIR%" (
    echo 🗑️ 기존 배포 폴더 삭제 중...
    rmdir /s /q "%DEPLOY_DIR%"
)
mkdir "%DEPLOY_DIR%"

REM 현재 프론트엔드 디렉토리에서 배포용 폴더로 파일 복사
cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend"

echo 📋 필요한 파일들 복사 중...
xcopy "src" "%DEPLOY_DIR%\src\" /E /I /H /Y
xcopy "public" "%DEPLOY_DIR%\public\" /E /I /H /Y
xcopy "package.json" "%DEPLOY_DIR%\" /Y
xcopy "tsconfig.json" "%DEPLOY_DIR%\" /Y
xcopy ".env.production" "%DEPLOY_DIR%\" /Y
xcopy "vercel.json" "%DEPLOY_DIR%\" /Y
xcopy "theme" "%DEPLOY_DIR%\theme\" /E /I /H /Y

REM README.md 복사 (있다면)
if exist "README.md" xcopy "README.md" "%DEPLOY_DIR%\" /Y

REM 불필요한 개발 파일 제외 (.env는 개발용이므로 제외)
if exist "%DEPLOY_DIR%\.env" del "%DEPLOY_DIR%\.env"

cd /d "%DEPLOY_DIR%"

echo ⚙️ package.json 최적화 중...
powershell -Command "(Get-Content package.json) -replace '\"private\": true,', '\"private\": false, \"homepage\": \".\",'; | Set-Content package.json"

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
echo ✅ 배포 준비 완료!
echo.
echo 📍 배포용 파일 위치: %DEPLOY_DIR%
echo.
echo 🎯 다음 단계를 수행하세요:
echo.
echo 1. GitHub 새 저장소 생성:
echo    - github.com 접속
echo    - New repository 클릭
echo    - Repository name: airiss-v4-frontend
echo    - ✅ Public 선택
echo    - Create repository 클릭
echo.
echo 2. GitHub에 코드 업로드:
echo    git branch -M main
echo    git remote add origin https://github.com/[YOUR-USERNAME]/airiss-v4-frontend.git
echo    git push -u origin main
echo.
echo 3. Vercel 배포:
echo    - vercel.com 접속
echo    - Continue with GitHub
echo    - New Project 클릭
echo    - airiss-v4-frontend 저장소 선택
echo    - Deploy 클릭
echo.
echo 🌐 배포 완료 후 테스트:
echo    - 메인 페이지 로딩 확인
echo    - 라우팅 동작 확인
echo    - 모바일 반응형 확인
echo.
pause
