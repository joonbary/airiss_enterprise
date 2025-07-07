# EMERGENCY_RECOVERY.ps1 - 긴급 복구 스크립트
# AIRISS 배포 실패 긴급 복구

Write-Host "🚨 AIRISS 긴급 복구 스크립트 시작" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Yellow
Write-Host ""

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "🕐 시작 시간: $timestamp" -ForegroundColor Cyan
Write-Host ""

# Step 1: 상세 에러 로그 확인
Write-Host "📋 Step 1: 상세 에러 로그 분석" -ForegroundColor Green
Write-Host "-------------------------------" -ForegroundColor Gray
Write-Host "최근 에러 로그 확인 중..." -ForegroundColor Yellow

try {
    $errorLogs = eb logs --all | Select-String -Pattern "ERROR|FAIL|Exception|failed|error" | Select-Object -Last 10
    if ($errorLogs) {
        Write-Host "🔍 발견된 에러들:" -ForegroundColor Red
        $errorLogs | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    } else {
        Write-Host "❓ 명확한 에러 로그를 찾을 수 없습니다." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ 로그 조회 중 오류 발생: $_" -ForegroundColor Red
}

Write-Host ""

# Step 2: 현재 배포 상태 확인
Write-Host "📋 Step 2: 배포 상태 진단" -ForegroundColor Green
Write-Host "------------------------" -ForegroundColor Gray

try {
    Write-Host "현재 애플리케이션 버전 확인..." -ForegroundColor Yellow
    eb list
    eb status
} catch {
    Write-Host "⚠️ 상태 확인 중 오류: $_" -ForegroundColor Red
}

Write-Host ""

# Step 3: 긴급 재배포 시도
Write-Host "📋 Step 3: 긴급 재배포 시도" -ForegroundColor Green
Write-Host "-------------------------" -ForegroundColor Gray

# 3-1: 간단한 application.py로 긴급 배포
Write-Host "3-1: 최소 버전으로 긴급 배포 준비..." -ForegroundColor Yellow

# 기존 application.py 백업
$backupTime = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "application.py" "application_backup_$backupTime.py" -Force
Write-Host "✅ 기존 파일 백업 완료: application_backup_$backupTime.py" -ForegroundColor Green

# 최소 버전 생성
@"
# EMERGENCY_APPLICATION.PY - 긴급 복구용 최소 버전
import os
import sys
import logging

# 기본 로깅
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
except ImportError as e:
    logger.error(f"FastAPI import failed: {e}")
    sys.exit(1)

# 최소 앱 생성
app = FastAPI(title="AIRISS Emergency Recovery", version="emergency-1.0")

@app.get("/")
async def root():
    return {"status": "emergency_recovery", "message": "AIRISS Emergency Mode"}

@app.get("/health")
async def health():
    return PlainTextResponse("OK", status_code=200)

@app.get("/status") 
async def status():
    return {"status": "emergency", "pid": os.getpid()}

# AWS EB 호환성
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
"@ | Out-File -FilePath "application_emergency.py" -Encoding UTF8

Write-Host "✅ 긴급 복구용 application.py 생성 완료" -ForegroundColor Green

# 긴급 버전으로 교체
Copy-Item "application_emergency.py" "application.py" -Force
Write-Host "✅ 긴급 버전으로 교체 완료" -ForegroundColor Green

Write-Host ""

# 3-2: 긴급 배포 실행
Write-Host "3-2: 긴급 배포 실행..." -ForegroundColor Yellow

try {
    Write-Host "🚀 긴급 배포 시작..." -ForegroundColor Cyan
    eb deploy --timeout=15
    
    Write-Host "⏳ 배포 완료 대기 (60초)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    
    Write-Host "✅ 긴급 배포 완료" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 긴급 배포 실패: $_" -ForegroundColor Red
    Write-Host "🔄 환경 재시작 시도..." -ForegroundColor Yellow
    
    try {
        eb restart
        Start-Sleep -Seconds 30
        Write-Host "✅ 환경 재시작 완료" -ForegroundColor Green
    } catch {
        Write-Host "❌ 환경 재시작도 실패: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Step 4: 복구 결과 확인
Write-Host "📋 Step 4: 복구 결과 확인" -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Gray

try {
    Write-Host "Health 상태 확인..." -ForegroundColor Yellow
    eb health --refresh
    
    Write-Host "전체 상태 확인..." -ForegroundColor Yellow  
    eb status
    
} catch {
    Write-Host "⚠️ 상태 확인 중 오류: $_" -ForegroundColor Red
}

Write-Host ""

# Step 5: 엔드포인트 테스트
Write-Host "📋 Step 5: 엔드포인트 직접 테스트" -ForegroundColor Green
Write-Host "-------------------------------" -ForegroundColor Gray

$url = "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com"

try {
    Write-Host "Root endpoint 테스트..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/" -TimeoutSec 10
    Write-Host "✅ Root: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root endpoint 실패: $_" -ForegroundColor Red
}

try {
    Write-Host "Health endpoint 테스트..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 10
    Write-Host "✅ Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health endpoint 실패: $_" -ForegroundColor Red
}

Write-Host ""

# 최종 결과
Write-Host "📋 긴급 복구 완료!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Yellow

$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "🕐 완료 시간: $endTime" -ForegroundColor Cyan

Write-Host ""
Write-Host "📞 다음 단계:" -ForegroundColor Cyan
Write-Host "1. Health가 Green으로 변경되었는지 확인" -ForegroundColor White
Write-Host "2. 여전히 Red면 환경 완전 재구축 필요" -ForegroundColor White
Write-Host "3. 정상 복구 후 원래 application.py 복원" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to continue..."
