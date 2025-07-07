@echo off
echo 🚀 AIRISS AWS EB CLI 설정 및 배포 자동화 스크립트
echo =====================================================

echo.
echo 🔧 1단계: EB CLI 초기화
echo.

echo EB CLI가 설치되어 있는지 확인 중...
eb --version
if %errorlevel% neq 0 (
    echo ❌ EB CLI가 설치되지 않았습니다!
    echo 설치 방법: pip install awsebcli
    pause
    exit /b 1
)

echo.
echo ✅ EB CLI 설치 확인됨

echo.
echo 🌍 AWS 리전: ap-northeast-2 (서울)
echo 📦 애플리케이션: airiss-v4
echo 🐍 플랫폼: Python 3.9 running on 64bit Amazon Linux 2
echo.

echo EB 초기화 실행 중...
eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2"

echo.
echo 🚀 2단계: 환경 생성 및 배포
echo.

echo 기존 환경이 있는지 확인 중...
eb status
if %errorlevel% neq 0 (
    echo 새 환경을 생성합니다...
    eb create production --instance_type t3.micro
) else (
    echo 기존 환경에 배포합니다...
    eb deploy
)

echo.
echo ✅ 배포 완료!
echo.
echo 🌐 확인 URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com
echo.
echo 배포 상태 확인 중...
eb status
eb health

echo.
echo 🎉 AIRISS AWS 배포 완료!
pause
