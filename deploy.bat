@echo off
setlocal enabledelayedexpansion

REM AIRISS v4.0 Enhanced - Windows 웹 배포 스크립트

echo ==============================================
echo    AIRISS v4.0 Enhanced 웹 배포 스크립트
echo ==============================================
echo.

REM 환경 변수 설정
set AIRISS_VERSION=4.0.1
set DEPLOY_ENV=%1
if "%DEPLOY_ENV%"=="" set DEPLOY_ENV=production

set DOMAIN=%2
if "%DOMAIN%"=="" set DOMAIN=localhost

set PORT=%3
if "%PORT%"=="" set PORT=8002

echo 📋 배포 설정:
echo    버전: %AIRISS_VERSION%
echo    환경: %DEPLOY_ENV%
echo    도메인: %DOMAIN%
echo    포트: %PORT%
echo.

REM 1. 사전 요구사항 확인
echo 🔍 1. 사전 요구사항 확인 중...

REM Docker 확인
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker가 설치되지 않았습니다.
    echo 💡 Docker Desktop을 설치해주세요: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Docker Compose 확인
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose가 설치되지 않았습니다.
    echo 💡 Docker Desktop에 포함되어 있습니다.
    pause
    exit /b 1
)

echo ✅ Docker 및 Docker Compose 확인 완료
echo.

REM 2. 기존 컨테이너 정리
echo 🧹 2. 기존 AIRISS 컨테이너 정리 중...

docker ps -q -f name=airiss >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ 기존 AIRISS 컨테이너를 중지합니다...
    docker-compose down
)

echo ✅ 컨테이너 정리 완료
echo.

REM 3. 이미지 빌드
echo 🔨 3. AIRISS v%AIRISS_VERSION% 이미지 빌드 중...

if "%DEPLOY_ENV%"=="development" (
    docker-compose build --no-cache
) else (
    docker-compose -f docker-compose.yml build --no-cache
)

if errorlevel 1 (
    echo ❌ 이미지 빌드 실패
    pause
    exit /b 1
)

echo ✅ 이미지 빌드 완료
echo.

REM 4. 환경 설정 파일 생성
echo ⚙️ 4. 환경 설정 파일 생성 중...

(
echo # AIRISS v4.0 Enhanced 환경 설정
echo AIRISS_ENV=%DEPLOY_ENV%
echo SERVER_HOST=0.0.0.0
echo SERVER_PORT=%PORT%
echo WS_HOST=%DOMAIN%
echo DOMAIN=%DOMAIN%
echo.
echo # 보안 설정
echo SECRET_KEY=airiss-enhanced-production-key-2024
echo CORS_ORIGINS=http://%DOMAIN%:%PORT%,https://%DOMAIN%
echo.
echo # 데이터베이스 설정
echo DB_PATH=/app/data/airiss.db
echo.
echo # 로그 설정
echo LOG_LEVEL=INFO
echo LOG_FILE=/app/logs/airiss.log
echo.
echo # 생성 시간
echo CREATED_AT=%DATE% %TIME%
) > .env

echo ✅ 환경 설정 파일 생성 완료
echo.

REM 5. 컨테이너 시작
echo 🚀 5. AIRISS v%AIRISS_VERSION% 컨테이너 시작 중...

if "%DEPLOY_ENV%"=="development" (
    docker-compose up -d
) else (
    docker-compose -f docker-compose.yml up -d
)

if errorlevel 1 (
    echo ❌ 컨테이너 시작 실패
    echo 💡 로그를 확인해주세요: docker-compose logs airiss-app
    pause
    exit /b 1
)

echo ✅ 컨테이너 시작 완료
echo.

REM 6. 헬스체크
echo 💊 6. 서비스 헬스체크 중...

set max_attempts=30
set attempt=1

:healthcheck_loop
curl -f http://localhost:%PORT%/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ 헬스체크 통과 ^(시도 !attempt!/%max_attempts%^)
    goto healthcheck_success
)

echo ⏳ 헬스체크 대기 중... ^(시도 !attempt!/%max_attempts%^)
timeout /t 2 >nul

set /a attempt+=1
if !attempt! leq %max_attempts% goto healthcheck_loop

echo ❌ 헬스체크 실패 - 서비스가 정상적으로 시작되지 않았습니다.
echo 💡 로그를 확인해주세요: docker-compose logs airiss-app
pause
exit /b 1

:healthcheck_success

REM 7. 배포 완료 정보 출력
echo.
echo ==============================================
echo ✅ AIRISS v%AIRISS_VERSION% 배포 완료!
echo ==============================================
echo.
echo 📋 접속 정보:
echo    🌐 메인 UI ^(Enhanced^): http://%DOMAIN%:%PORT%/
echo    📊 개발자 대시보드:      http://%DOMAIN%:%PORT%/dashboard
echo    📖 API 문서:            http://%DOMAIN%:%PORT%/docs
echo    💊 헬스체크:            http://%DOMAIN%:%PORT%/health
echo.
echo 🐳 Docker 명령어:
echo    컨테이너 상태 확인:      docker-compose ps
echo    로그 확인:              docker-compose logs -f airiss-app
echo    컨테이너 중지:          docker-compose down
echo    컨테이너 재시작:        docker-compose restart
echo.
echo 📁 데이터 위치:
echo    SQLite DB:             /app/data/airiss.db
echo    업로드 파일:           /app/uploads/
echo    로그 파일:             /app/logs/
echo.
echo 🔧 관리 도구:
echo    모니터링:              docker stats airiss-v4-enhanced
echo    데이터 백업:           docker exec airiss-v4-enhanced cp /app/data/airiss.db /backup/
echo.
echo ⚠️ 중요: 프로덕션 환경에서는 HTTPS 설정과 방화벽 구성을 완료해주세요.
echo.
echo ✅ 배포 스크립트 완료!
echo.

REM 브라우저 자동 실행 (선택사항)
echo 🌐 브라우저에서 AIRISS를 열겠습니까? ^(Y/N^)
set /p open_browser=

if /i "%open_browser%"=="Y" (
    start http://localhost:%PORT%/
    echo 🚀 브라우저에서 AIRISS v4.0 Enhanced가 열렸습니다!
)

echo.
echo 📋 배포 완료! 엔터를 눌러 종료하세요.
pause >nul
