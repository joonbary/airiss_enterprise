@echo off
echo AIRISS v4 AWS EB 배포 시작...

REM 1. EB CLI 확인
where eb >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo EB CLI가 설치되지 않았습니다.
    echo pip install awsebcli 로 설치하세요.
    exit /b 1
)

REM 2. 현재 상태 확인
echo 현재 EB 환경 상태 확인...
eb status

REM 3. 배포 실행
echo 배포 실행 중...
eb deploy

REM 4. 상태 확인
echo 배포 완료 - 상태 확인...
eb status
eb health

echo 배포 완료! 
eb open
