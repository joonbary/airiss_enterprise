# IMMEDIATE_FIX.ps1 - PowerShell용 즉시 해결 스크립트
# AIRISS Health Red 즉시 해결

Write-Host "🚨 AIRISS Health Red 즉시 해결 스크립트" -ForegroundColor Red
Write-Host "================================================" -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date
Write-Host "⏰ 시작 시간: $startTime" -ForegroundColor Cyan
Write-Host "📍 현재 위치: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

Write-Host "1️⃣ 현재 EB 상태 확인" -ForegroundColor Green
Write-Host "---------------------------" -ForegroundColor Gray
eb status

Write-Host ""
Write-Host "2️⃣ 상세 헬스 정보 조회" -ForegroundColor Green
Write-Host "------------------------" -ForegroundColor Gray
eb health --refresh

Write-Host ""
Write-Host "3️⃣ 최근 로그 확인 (마지막 50줄)" -ForegroundColor Green
Write-Host "-------------------------------" -ForegroundColor Gray
eb logs --all | Select-Object -Last 50

Write-Host ""
Write-Host "4️⃣ 애플리케이션 재시작 시도" -ForegroundColor Green
Write-Host "----------------------------" -ForegroundColor Gray
eb restart

Write-Host ""
Write-Host "⏳ 30초 대기 (재시작 완료 대기)" -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "5️⃣ 재시작 후 상태 확인" -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Gray
eb health --refresh

Write-Host ""
Write-Host "6️⃣ URL 테스트" -ForegroundColor Green
Write-Host "-------------" -ForegroundColor Gray
eb open

Write-Host ""
Write-Host "✅ 즉시 해결 시도 완료!" -ForegroundColor Green
Write-Host "📋 Health가 여전히 Red면 로그를 확인하여 근본 원인 파악 필요" -ForegroundColor Yellow

$endTime = Get-Date
$duration = $endTime - $startTime
Write-Host "⏱️ 총 소요 시간: $($duration.TotalMinutes.ToString('F1'))분" -ForegroundColor Cyan

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
