# AIRISS v4.0 React Integration Setup
# PowerShell 스크립트 버전

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "   AIRISS v4.0 React Integration Setup" -ForegroundColor Yellow  
Write-Host "========================================" -ForegroundColor Yellow
Write-Host

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🚀 AIRISS v4.0 React 통합 개발 환경 시작" -ForegroundColor Green
Write-Host "📁 프로젝트 루트: $PROJECT_ROOT" -ForegroundColor Cyan
Write-Host

# 백엔드 서버 실행 (백그라운드)
Write-Host "🔧 백엔드 서버 시작 중..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    param($rootPath)
    Set-Location $rootPath
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
} -ArgumentList $PROJECT_ROOT

# 3초 대기
Start-Sleep -Seconds 3

# React 개발 서버 실행
Write-Host "🌐 React 개발 서버 시작 중..." -ForegroundColor Blue
$frontendPath = Join-Path $PROJECT_ROOT "airiss-v4-frontend"

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ React 앱 디렉토리를 찾을 수 없습니다: $frontendPath" -ForegroundColor Red
    exit 1
}

Set-Location $frontendPath

# npm 설치 확인
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Node modules가 없습니다. npm install을 실행합니다..." -ForegroundColor Yellow
    npm install
}

# React 개발 서버 시작
Write-Host "🚀 React 앱 시작..." -ForegroundColor Green
Write-Host
Write-Host "========================================" -ForegroundColor Green
Write-Host "   AIRISS v4.0 개발 환경이 실행되었습니다!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "🌐 React 앱: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 백엔드 API: http://localhost:8002" -ForegroundColor Cyan
Write-Host "📖 API 문서: http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "📊 개발 대시보드: http://localhost:8002/dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
Write-Host

try {
    npm start
}
catch {
    Write-Host "❌ React 앱 시작 실패: $_" -ForegroundColor Red
}
finally {
    # 백그라운드 작업 정리
    if ($backendJob) {
        Stop-Job $backendJob
        Remove-Job $backendJob
        Write-Host "🛑 백엔드 서버 종료됨" -ForegroundColor Yellow
    }
}

Write-Host "✅ 개발 환경 종료 완료" -ForegroundColor Green