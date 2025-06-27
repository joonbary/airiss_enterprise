@echo off
REM AIRISS v4.0 Windows 고급 배포 스크립트
setlocal enabledelayedexpansion

title AIRISS v4.0 Advanced Deployment for Windows

REM 색상 코드 설정
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

REM 기본값 설정
set "ENVIRONMENT=%1"
set "DOMAIN=%2"
set "PORT=%3"
set "ENABLE_SSL=false"
set "ENABLE_MONITORING=false"
set "ENABLE_BACKUP=false"
set "DEPLOY_REACT=false"

if "%ENVIRONMENT%"=="" set "ENVIRONMENT=development"
if "%DOMAIN%"=="" set "DOMAIN=localhost"
if "%PORT%"=="" set "PORT=8002"

REM 옵션 파싱
:parse_options
if "%4"=="" goto :start_deployment
if "%4"=="--ssl" set "ENABLE_SSL=true"
if "%4"=="--monitoring" set "ENABLE_MONITORING=true"
if "%4"=="--backup" set "ENABLE_BACKUP=true"
if "%4"=="--react" set "DEPLOY_REACT=true"
if "%4"=="--help" goto :show_help
shift
goto :parse_options

:show_help
echo %BLUE%AIRISS v4.0 Advanced Deployment Script for Windows%RESET%
echo.
echo 사용법: %0 [환경] [도메인] [포트] [옵션들]
echo.
echo 환경:
echo   development  - 개발 환경 (기본값)
echo   staging      - 스테이징 환경  
echo   production   - 프로덕션 환경
echo.
echo 옵션:
echo   --ssl        - HTTPS 설정 활성화
echo   --monitoring - 모니터링 도구 설치
echo   --backup     - 데이터베이스 백업 설정
echo   --react      - React 앱도 함께 배포
echo   --help       - 이 도움말 표시
echo.
echo 예시:
echo   %0 development localhost 8002
echo   %0 production airiss.okfinancial.com 443 --ssl --monitoring
echo   %0 staging staging.airiss.com 8002 --react --backup
echo.
pause
exit /b 0

:start_deployment
echo %BLUE%[INFO]%RESET% 🚀 AIRISS v4.0 Advanced Deployment 시작
echo ===============================================
echo 환경: %ENVIRONMENT%
echo 도메인: %DOMAIN%
echo 포트: %PORT%
echo SSL: %ENABLE_SSL%
echo 모니터링: %ENABLE_MONITORING%
echo 백업: %ENABLE_BACKUP%
echo React 배포: %DEPLOY_REACT%
echo ===============================================
echo.

REM 필수 도구 확인
echo %BLUE%[INFO]%RESET% 필수 도구 확인 중...

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Docker가 설치되지 않았습니다.
    echo Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Docker Compose가 설치되지 않았습니다.
    pause
    exit /b 1
)

if "%DEPLOY_REACT%"=="true" (
    where node >nul 2>&1
    if !errorlevel! neq 0 (
        echo %RED%[ERROR]%RESET% Node.js가 설치되지 않았습니다.
        echo Node.js를 설치해주세요: https://nodejs.org/
        pause
        exit /b 1
    )
    
    where npm >nul 2>&1
    if !errorlevel! neq 0 (
        echo %RED%[ERROR]%RESET% npm이 설치되지 않았습니다.
        pause
        exit /b 1
    )
)

echo %GREEN%[SUCCESS]%RESET% 모든 필수 도구가 설치되어 있습니다.
echo.

REM 환경별 설정
set "COMPOSE_FILE=docker-compose.yml"
set "BUILD_TARGET=development"
set "REPLICAS=1"

if "%ENVIRONMENT%"=="staging" (
    set "COMPOSE_FILE=docker-compose.staging.yml"
    set "BUILD_TARGET=staging"
    set "REPLICAS=2"
)

if "%ENVIRONMENT%"=="production" (
    set "COMPOSE_FILE=docker-compose.production.yml"
    set "BUILD_TARGET=production"
    set "REPLICAS=3"
)

REM Docker Compose 파일 생성
echo %BLUE%[INFO]%RESET% Docker Compose 파일 생성 중...

(
echo version: '3.8'
echo.
echo services:
echo   airiss-app:
echo     build:
echo       context: .
echo       dockerfile: Dockerfile
echo       target: %BUILD_TARGET%
echo     ports:
echo       - "%PORT%:8002"
echo     environment:
echo       - ENVIRONMENT=%ENVIRONMENT%
echo       - SERVER_HOST=0.0.0.0
echo       - SERVER_PORT=8002
echo       - WS_HOST=%DOMAIN%
echo     volumes:
echo       - airiss_data:/app/data
echo       - airiss_logs:/app/logs
echo       - airiss_uploads:/app/uploads
echo     restart: unless-stopped
echo     healthcheck:
echo       test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
echo       interval: 30s
echo       timeout: 10s
echo       retries: 3
echo       start_period: 40s
) > %COMPOSE_FILE%

REM React 앱 설정 추가
if "%DEPLOY_REACT%"=="true" (
    (
    echo.
    echo   airiss-frontend:
    echo     build:
    echo       context: ./airiss-v4-frontend
    echo       dockerfile: Dockerfile.react
    echo     ports:
    echo       - "3000:3000"
    echo     environment:
    echo       - REACT_APP_API_URL=http://%DOMAIN%:%PORT%
    echo     depends_on:
    echo       - airiss-app
    echo     restart: unless-stopped
    ) >> %COMPOSE_FILE%
)

REM SSL 설정 추가
if "%ENABLE_SSL%"=="true" (
    (
    echo.
    echo   nginx:
    echo     image: nginx:alpine
    echo     ports:
    echo       - "80:80"
    echo       - "443:443"
    echo     volumes:
    echo       - ./nginx.conf:/etc/nginx/nginx.conf:ro
    echo       - ./ssl:/etc/nginx/ssl:ro
    echo     depends_on:
    echo       - airiss-app
    echo     restart: unless-stopped
    ) >> %COMPOSE_FILE%
)

REM 모니터링 설정 추가
if "%ENABLE_MONITORING%"=="true" (
    (
    echo.
    echo   prometheus:
    echo     image: prom/prometheus:latest
    echo     ports:
    echo       - "9090:9090"
    echo     volumes:
    echo       - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    echo       - prometheus_data:/prometheus
    echo     restart: unless-stopped
    echo.
    echo   grafana:
    echo     image: grafana/grafana:latest
    echo     ports:
    echo       - "3001:3000"
    echo     environment:
    echo       - GF_SECURITY_ADMIN_PASSWORD=admin123
    echo     volumes:
    echo       - grafana_data:/var/lib/grafana
    echo     restart: unless-stopped
    ) >> %COMPOSE_FILE%
)

REM 볼륨 설정 추가
(
echo.
echo volumes:
echo   airiss_data:
echo   airiss_logs:
echo   airiss_uploads:
) >> %COMPOSE_FILE%

if "%ENABLE_MONITORING%"=="true" (
    (
    echo   prometheus_data:
    echo   grafana_data:
    ) >> %COMPOSE_FILE%
)

echo %GREEN%[SUCCESS]%RESET% Docker Compose 파일이 생성되었습니다: %COMPOSE_FILE%
echo.

REM Nginx 설정 파일 생성 (SSL 사용 시)
if "%ENABLE_SSL%"=="true" (
    echo %BLUE%[INFO]%RESET% Nginx SSL 설정 파일 생성 중...
    
    if not exist ssl mkdir ssl
    
    (
    echo events {
    echo     worker_connections 1024;
    echo }
    echo.
    echo http {
    echo     upstream airiss_backend {
    echo         server airiss-app:8002;
    echo     }
    echo.
    echo     # HTTP to HTTPS redirect
    echo     server {
    echo         listen 80;
    echo         server_name %DOMAIN%;
    echo         return 301 https://$server_name$request_uri;
    echo     }
    echo.
    echo     # HTTPS server
    echo     server {
    echo         listen 443 ssl http2;
    echo         server_name %DOMAIN%;
    echo.
    echo         ssl_certificate /etc/nginx/ssl/fullchain.pem;
    echo         ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    echo.
    echo         location / {
    echo             proxy_pass http://airiss_backend;
    echo             proxy_set_header Host $host;
    echo             proxy_set_header X-Real-IP $remote_addr;
    echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    echo             proxy_set_header X-Forwarded-Proto $scheme;
    echo         }
    echo.
    echo         location /ws/ {
    echo             proxy_pass http://airiss_backend;
    echo             proxy_http_version 1.1;
    echo             proxy_set_header Upgrade $http_upgrade;
    echo             proxy_set_header Connection "upgrade";
    echo             proxy_set_header Host $host;
    echo             proxy_cache_bypass $http_upgrade;
    echo         }
    echo     }
    echo }
    ) > nginx.conf
    
    echo %GREEN%[SUCCESS]%RESET% Nginx 설정 파일이 생성되었습니다.
    echo %YELLOW%[WARNING]%RESET% SSL 인증서를 ssl\ 디렉토리에 배치해주세요:
    echo %YELLOW%[WARNING]%RESET%   - ssl\fullchain.pem
    echo %YELLOW%[WARNING]%RESET%   - ssl\privkey.pem
    echo.
)

REM React 앱 빌드
if "%DEPLOY_REACT%"=="true" (
    echo %BLUE%[INFO]%RESET% React 앱 빌드 중...
    
    cd airiss-v4-frontend
    
    REM 환경별 설정
    (
    echo REACT_APP_API_URL=http://%DOMAIN%:%PORT%
    echo REACT_APP_WS_URL=ws://%DOMAIN%:%PORT%
    echo REACT_APP_ENVIRONMENT=%ENVIRONMENT%
    ) > .env.production
    
    call npm ci
    call npm run build
    
    REM React용 Dockerfile 생성
    (
    echo FROM node:18-alpine as builder
    echo.
    echo WORKDIR /app
    echo COPY package*.json ./
    echo RUN npm ci --only=production
    echo.
    echo COPY . .
    echo RUN npm run build
    echo.
    echo FROM nginx:alpine
    echo COPY --from=builder /app/build /usr/share/nginx/html
    echo COPY nginx.react.conf /etc/nginx/conf.d/default.conf
    echo.
    echo EXPOSE 3000
    echo CMD ["nginx", "-g", "daemon off;"]
    ) > Dockerfile.react
    
    cd ..
    echo %GREEN%[SUCCESS]%RESET% React 앱 빌드가 완료되었습니다.
    echo.
)

REM 모니터링 설정
if "%ENABLE_MONITORING%"=="true" (
    echo %BLUE%[INFO]%RESET% 모니터링 설정 중...
    
    (
    echo global:
    echo   scrape_interval: 15s
    echo.
    echo scrape_configs:
    echo   - job_name: 'airiss-app'
    echo     static_configs:
    echo       - targets: ['airiss-app:8002']
    echo     metrics_path: '/metrics'
    echo     scrape_interval: 30s
    ) > prometheus.yml
    
    echo %GREEN%[SUCCESS]%RESET% 모니터링 설정이 완료되었습니다.
    echo.
)

REM 백업 스크립트 생성
if "%ENABLE_BACKUP%"=="true" (
    echo %BLUE%[INFO]%RESET% 백업 스크립트 생성 중...
    
    (
    echo @echo off
    echo REM AIRISS v4.0 백업 스크립트
    echo.
    echo set "BACKUP_DIR=C:\backup\airiss"
    echo set "DATE=%%date:~0,4%%%%date:~5,2%%%%date:~8,2%%_%%time:~0,2%%%%time:~3,2%%%%time:~6,2%%"
    echo set "DATE=%%DATE: =0%%"
    echo.
    echo if not exist %%BACKUP_DIR%% mkdir %%BACKUP_DIR%%
    echo.
    echo REM 데이터베이스 백업
    echo for /f %%%%i in ('docker ps -q -f "name=airiss-app"'^) do set CONTAINER_ID=%%%%i
    echo docker exec %%CONTAINER_ID%% cp /app/airiss.db /tmp/airiss_backup_%%DATE%%.db
    echo docker cp %%CONTAINER_ID%%:/tmp/airiss_backup_%%DATE%%.db %%BACKUP_DIR%%\
    echo.
    echo echo 백업 완료: %%DATE%%
    ) > backup.bat
    
    echo %GREEN%[SUCCESS]%RESET% 백업 스크립트가 생성되었습니다: backup.bat
    echo %YELLOW%[WARNING]%RESET% 자동 백업을 위해 작업 스케줄러에 등록하세요.
    echo.
)

REM 애플리케이션 배포
echo %BLUE%[INFO]%RESET% 애플리케이션 배포 중...

REM 기존 컨테이너 정리
if exist %COMPOSE_FILE% (
    docker-compose -f %COMPOSE_FILE% down 2>nul
)

REM 이미지 빌드 및 시작
docker-compose -f %COMPOSE_FILE% build
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Docker 빌드 실패
    pause
    exit /b 1
)

docker-compose -f %COMPOSE_FILE% up -d
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%RESET% Docker 시작 실패
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%RESET% 배포가 완료되었습니다.
echo.

REM 헬스 체크
echo %BLUE%[INFO]%RESET% 애플리케이션 헬스 체크 중...

set "max_attempts=30"
set "attempt=1"

:health_check_loop
curl -f http://%DOMAIN%:%PORT%/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[SUCCESS]%RESET% 애플리케이션이 정상적으로 실행 중입니다!
    goto :health_check_complete
)

echo %YELLOW%[WARNING]%RESET% 헬스 체크 시도 %attempt%/%max_attempts%...
timeout /t 5 /nobreak >nul

set /a attempt+=1
if %attempt% leq %max_attempts% goto :health_check_loop

echo %RED%[ERROR]%RESET% 헬스 체크 실패. 로그를 확인해주세요.
docker-compose -f %COMPOSE_FILE% logs --tail=50 airiss-app
pause
exit /b 1

:health_check_complete
echo.

REM 배포 후 정보 출력
echo %GREEN%[SUCCESS]%RESET% 🎉 AIRISS v4.0 배포가 완료되었습니다!
echo.
echo ===============================================
echo 📱 접속 정보:
if "%ENABLE_SSL%"=="true" (
    echo    메인 URL: https://%DOMAIN%
    echo    API 문서: https://%DOMAIN%/docs
    echo    대시보드: https://%DOMAIN%/dashboard
) else (
    echo    메인 URL: http://%DOMAIN%:%PORT%
    echo    API 문서: http://%DOMAIN%:%PORT%/docs
    echo    대시보드: http://%DOMAIN%:%PORT%/dashboard
)

if "%DEPLOY_REACT%"=="true" (
    echo    React 앱: http://%DOMAIN%:3000
)

if "%ENABLE_MONITORING%"=="true" (
    echo    모니터링: http://%DOMAIN%:3001 (Grafana)
    echo    메트릭: http://%DOMAIN%:9090 (Prometheus)
)

echo.
echo 🔧 관리 명령어:
echo    로그 확인: docker-compose -f %COMPOSE_FILE% logs -f
echo    서비스 재시작: docker-compose -f %COMPOSE_FILE% restart
echo    서비스 중지: docker-compose -f %COMPOSE_FILE% down

if "%ENABLE_BACKUP%"=="true" (
    echo    백업 실행: backup.bat
)

echo ===============================================
echo.
echo %GREEN%[SUCCESS]%RESET% 모든 배포 과정이 완료되었습니다! 🚀
echo.
pause