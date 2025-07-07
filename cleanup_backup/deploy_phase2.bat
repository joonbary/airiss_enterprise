@echo off
echo ========================================
echo AIRISS Phase 2 Core AWS Deployment
echo ========================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo [경고] Phase 2 배포를 시작합니다.
echo - Emergency 기능 유지
echo - Core 서비스 (DB + AI) 추가
echo - WebSocket은 Phase 3에서 활성화
echo.
set /p confirm="계속하시겠습니까? (y/N): "
if /i not "%confirm%"=="y" goto :cancel

echo.
echo [1/6] 현재 application.py 백업...
copy application.py application_backup_phase2_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py

echo.
echo [2/6] Phase 2 파일로 교체...
copy application_phase2_preparation.py application.py

echo.
echo [3/6] 가상환경 활성화...
call venv\Scripts\activate

echo.
echo [4/6] AWS EB CLI 확인...
eb --version
if errorlevel 1 (
    echo ❌ AWS EB CLI가 설치되지 않았습니다.
    echo pip install awsebcli 명령으로 설치하세요.
    goto :rollback
)

echo.
echo [5/6] AWS Elastic Beanstalk 배포...
eb deploy

if errorlevel 1 (
    echo ❌ 배포 실패!
    goto :rollback
)

echo.
echo [6/6] 배포 상태 확인...
eb status
eb health

echo.
echo ✅ Phase 2 배포 완료!
echo 🌐 Live URL: http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com
echo 📊 상태 확인: /status
echo 🗄️ DB 헬스: /health/db  
echo 🧠 AI 헬스: /health/analysis
echo.
echo Phase 3 예정: WebSocket + 고급 AI 기능
echo.
goto :end

:rollback
echo.
echo 🔄 롤백 중...
copy application_backup_phase2_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.py application.py
echo ✅ 롤백 완료

:cancel
echo 취소되었습니다.

:end
pause
