@echo off
echo ============================================
echo AIRISS v4 AWS 긴급 배포 (PID 오류 수정)
echo ============================================
echo.

echo [1/5] 배포 전 확인사항...
if not exist "application.py" (
    echo ❌ ERROR: application.py를 찾을 수 없습니다.
    echo 올바른 프로젝트 폴더에서 실행하세요.
    pause
    exit /b 1
)

echo [2/5] Procfile 검증...
findstr /C:"--pid" Procfile >nul
if %errorlevel% == 0 (
    echo ❌ ERROR: Procfile에 --pid 옵션이 아직 있습니다!
    echo 수동으로 제거하고 다시 실행하세요.
    pause
    exit /b 1
)
echo ✅ Procfile 확인 완료

echo [3/5] requirements.txt 확인...
if not exist "requirements.txt" (
    echo ❌ ERROR: requirements.txt를 찾을 수 없습니다.
    pause
    exit /b 1
)
echo ✅ requirements.txt 확인 완료

echo [4/5] AWS EB CLI 확인...
eb --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: AWS EB CLI가 설치되지 않았습니다.
    echo 다음 명령으로 설치하세요: pip install awsebcli
    pause
    exit /b 1
)
echo ✅ EB CLI 확인 완료

echo [5/5] 배포 시작...
echo.
echo 🚀 배포 중... (약 5-10분 소요)
echo.

eb deploy

if %errorlevel% == 0 (
    echo.
    echo ✅ 배포 성공!
    echo.
    echo 🌐 애플리케이션 URL:
    eb open
    echo.
    echo 📊 상태 확인:
    eb status
    echo.
    echo 📝 로그 확인 (문제가 있다면):
    echo eb logs --all
) else (
    echo.
    echo ❌ 배포 실패!
    echo.
    echo 🔍 상세 로그 확인:
    eb logs --all
    echo.
    echo 💡 문제 해결 단계:
    echo 1. Procfile에서 --pid와 --daemon-off 옵션 제거 확인
    echo 2. .ebextensions/python_final.config 확인
    echo 3. application.py 파일 존재 확인
    echo 4. eb logs로 상세 에러 확인
)

echo.
echo ============================================
echo 배포 완료
echo ============================================
pause
