@echo off
echo 🚀 AWS CLI 자동 설치 및 AIRISS 배포 스크립트
echo =============================================

echo.
echo 📦 1단계: AWS CLI 설치 중...
echo.

pip install awscli
if %errorlevel% neq 0 (
    echo ❌ pip을 통한 AWS CLI 설치 실패
    echo 대안: https://aws.amazon.com/cli/ 에서 수동 설치
    pause
    exit /b 1
)

echo ✅ AWS CLI 설치 완료!

echo.
echo 🔑 2단계: AWS 자격 증명 설정
echo.
echo AWS 콘솔에서 다음 정보를 준비하세요:
echo - Access Key ID
echo - Secret Access Key
echo.

aws configure

echo.
echo 🧪 3단계: 설정 확인
echo.

aws sts get-caller-identity
if %errorlevel% neq 0 (
    echo ❌ AWS 자격 증명 설정에 문제가 있습니다
    echo 다시 설정해보세요: aws configure
    pause
    exit /b 1
)

echo ✅ AWS 자격 증명 설정 완료!

echo.
echo 🚀 4단계: AIRISS EB 초기화 및 배포
echo.

eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2" airiss-v4

echo.
echo 환경 생성 및 배포 중...
echo.

eb create production --instance_type t3.micro

echo.
echo ✅ AIRISS AWS 배포 완료!
echo 🌐 URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com
echo.

eb status
eb open

pause
