@echo off
echo ==========================================
echo    AIRISS v4.1 AWS 최적화 배포 스크립트
echo ==========================================
echo 🚀 배포 시작: %date% %time%

:: 현재 설정 확인
echo.
echo 📋 현재 설정 확인...
echo Procfile 설정:
type Procfile
echo.
echo .ebextensions 설정:
if exist .ebextensions\python_final.config (
    echo ✅ python_final.config 파일 존재
) else (
    echo ❌ python_final.config 파일 없음
)

:: Git 상태 확인
echo.
echo 📊 Git 상태 확인...
git status --porcelain
if %errorlevel% neq 0 (
    echo ❌ Git 저장소 초기화 필요
    git init
    git add .
)

:: 변경사항 커밋
echo.
echo 💾 변경사항 커밋...
git add .
git commit -m "AWS 배포 최적화: PID 파일 생성 및 헬스체크 개선 - %date% %time%"

:: EB CLI 환경 확인
echo.
echo 🔍 EB CLI 환경 확인...
eb status
if %errorlevel% neq 0 (
    echo ❌ EB 환경 설정이 필요합니다
    echo eb init을 먼저 실행하세요
    pause
    exit /b 1
)

:: 배포 시작
echo.
echo 🚀 AWS Elastic Beanstalk 배포 시작...
echo 📝 주요 개선사항:
echo    - Procfile: PID 파일 경로 명시, timeout 300초
echo    - .ebextensions: PID 디렉토리 생성, 헬스체크 300초 유예
echo    - container_commands: 필요 디렉토리 사전 생성
echo.

:: 타임아웃을 길게 설정한 배포
eb deploy --timeout=20
if %errorlevel% neq 0 (
    echo.
    echo ❌ 배포 실패! 
    echo 🔧 트러블슈팅 단계:
    echo 1. eb logs 명령으로 로그 확인
    echo 2. eb status로 현재 상태 확인  
    echo 3. eb health로 헬스체크 상태 확인
    echo.
    pause
    exit /b 1
)

:: 배포 성공 후 확인
echo.
echo ✅ 배포 완료!
echo 🔍 배포 상태 확인 중...

:: EB 상태 확인
eb status

:: 헬스체크 확인
echo.
echo 💓 애플리케이션 헬스체크 확인...
eb health

:: URL 확인
echo.
echo 🌐 애플리케이션 URL:
eb status | findstr "CNAME"

echo.
echo ==========================================
echo ✅ AIRISS v4.1 배포 완료!
echo ==========================================
echo 📅 완료 시간: %date% %time%
echo 🔗 다음 단계:
echo    1. eb open 명령으로 브라우저에서 확인
echo    2. /health 엔드포인트 테스트
echo    3. 로그 모니터링: eb logs
echo ==========================================

pause
