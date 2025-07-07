@echo off
echo ========================================
echo 🚨 AIRISS v4 긴급 AWS 배포 수정 스크립트
echo ========================================

echo.
echo ⏱️ Step 1: 안전한 Procfile로 교체 중...
copy /Y Procfile_emergency Procfile
if %errorlevel% equ 0 (
    echo ✅ Procfile 교체 완료
) else (
    echo ❌ Procfile 교체 실패
    pause
    exit /b 1
)

echo.
echo 📦 Step 2: 새로운 배포 패키지 생성 중...
del /Q "airiss_v4_emergency_fix_%date:~0,4%%date:~5,2%%date:~8,2%.zip" 2>nul

echo 📁 필수 파일만 포함하여 압축...
tar -czf "airiss_v4_emergency_fix_%date:~0,4%%date:~5,2%%date:~8,2%.zip" ^
    --exclude=".git" ^
    --exclude="venv" ^
    --exclude="__pycache__" ^
    --exclude="*.log" ^
    --exclude="node_modules" ^
    --exclude="test_*" ^
    --exclude="backup_*" ^
    --exclude="*.bat" ^
    --exclude="*.ps1" ^
    application.py ^
    Procfile ^
    requirements.txt ^
    runtime.txt ^
    .ebextensions/ ^
    app/

if %errorlevel% equ 0 (
    echo ✅ 배포 패키지 생성 완료
) else (
    echo ❌ 배포 패키지 생성 실패
    pause
    exit /b 1
)

echo.
echo 🚀 Step 3: AWS EB 배포 실행...
echo 📌 배포 모니터링: https://console.aws.amazon.com/elasticbeanstalk

eb deploy --timeout 10

if %errorlevel% equ 0 (
    echo.
    echo ✅========================================
    echo ✅ 긴급 배포 성공!
    echo ✅========================================
    echo.
    echo 🔗 애플리케이션 URL 확인:
    eb open
    echo.
    echo 📊 실시간 로그 모니터링:
    echo eb logs --all
    echo.
    echo 💡 헬스체크 URL:
    echo https://your-app-url/health
    echo.
) else (
    echo.
    echo ❌========================================
    echo ❌ 배포 실패 - 추가 조치 필요
    echo ❌========================================
    echo.
    echo 🔧 즉시 실행할 명령어:
    echo 1. eb logs --all
    echo 2. eb health
    echo 3. eb status
    echo.
    echo 🆘 긴급 롤백:
    echo eb deploy --version [이전-버전-라벨]
    echo.
)

echo 📋 배포 후 확인사항:
echo - 헬스체크: /health 엔드포인트 응답 확인
echo - 메인페이지: / 루트 엔드포인트 응답 확인
echo - 로그 상태: PID 파일 생성 오류 해결 확인

pause