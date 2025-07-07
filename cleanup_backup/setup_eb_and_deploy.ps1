# AIRISS AWS EB CLI 설정 및 배포 PowerShell 스크립트

Write-Host "🚀 AIRISS AWS EB CLI 설정 및 배포 자동화 스크립트" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔧 1단계: EB CLI 설치 확인" -ForegroundColor Yellow
Write-Host ""

# EB CLI 버전 확인
try {
    $ebVersion = eb --version
    Write-Host "✅ EB CLI 설치 확인됨: $ebVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ EB CLI가 설치되지 않았습니다!" -ForegroundColor Red
    Write-Host "설치 방법: pip install awsebcli" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "🌍 AWS 리전: ap-northeast-2 (서울)" -ForegroundColor Cyan
Write-Host "📦 애플리케이션: airiss-v4" -ForegroundColor Cyan
Write-Host "🐍 플랫폼: Python 3.9 running on 64bit Amazon Linux 2" -ForegroundColor Cyan
Write-Host ""

Write-Host "EB 초기화 실행 중..." -ForegroundColor Yellow
eb init --region ap-northeast-2 --platform "Python 3.9 running on 64bit Amazon Linux 2" airiss-v4

Write-Host ""
Write-Host "🚀 2단계: 환경 상태 확인" -ForegroundColor Yellow
Write-Host ""

# 환경 상태 확인
try {
    eb status
    Write-Host "기존 환경에 배포합니다..." -ForegroundColor Green
    eb deploy
} catch {
    Write-Host "새 환경을 생성합니다..." -ForegroundColor Yellow
    eb create production --instance_type t3.micro
}

Write-Host ""
Write-Host "✅ 배포 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 확인 URL: https://airiss-v4.ap-northeast-2.elasticbeanstalk.com" -ForegroundColor Cyan
Write-Host ""

Write-Host "배포 상태 확인 중..." -ForegroundColor Yellow
eb status
eb health

Write-Host ""
Write-Host "🎉 AIRISS AWS 배포 완료!" -ForegroundColor Green
Read-Host "계속하려면 Enter를 누르세요"
