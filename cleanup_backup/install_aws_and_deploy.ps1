# AWS CLI 설치 및 AIRISS 배포 PowerShell 스크립트

Write-Host "🚀 AWS CLI 설치 및 AIRISS 배포 자동화" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "📦 1단계: AWS CLI 설치 중..." -ForegroundColor Yellow

try {
    pip install awscli
    Write-Host "✅ AWS CLI 설치 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI 설치 실패" -ForegroundColor Red
    Write-Host "대안: https://aws.amazon.com/cli/ 에서 수동 설치" -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""
Write-Host "🔑 2단계: AWS 자격 증명 설정" -ForegroundColor Yellow
Write-Host ""
Write-Host "AWS 콘솔에서 다음 정보를 준비하세요:" -ForegroundColor Cyan
Write-Host "- Access Key ID" -ForegroundColor Cyan
Write-Host "- Secret Access Key" -ForegroundColor Cyan
Write-Host ""

aws configure

Write-Host ""
Write-Host "🧪 3단계: 설정 확인" -ForegroundColor Yellow

try {
    aws sts get-caller-identity
    Write-Host "✅ AWS 자격 증명 설정 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS 자격 증명 설정에 문제가 있습니다" -ForegroundColor Red
    Write-Host "다시 설정해보세요: aws configure" -ForegroundColor Yellow
    Read-Host "계속하려면 Enter를 누르세요"
    exit 1
}

Write-Host ""
Write-Host "🚀 4단계: AIRISS EB 초기화 및 배포" -ForegroundColor Yellow

eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2" airiss-v4

Write-Host ""
Write-Host "환경 생성 및 배포 중..." -ForegroundColor Yellow

eb create production --instance_type t3.micro

Write-Host ""
Write-Host "✅ AIRISS AWS 배포 완료!" -ForegroundColor Green
Write-Host "🌐 URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com" -ForegroundColor Cyan

eb status
eb open

Read-Host "완료! 계속하려면 Enter를 누르세요"
