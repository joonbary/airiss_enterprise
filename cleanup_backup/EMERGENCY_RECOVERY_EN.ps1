# EMERGENCY_RECOVERY_EN.ps1 - English Version Emergency Recovery
# AIRISS Emergency Recovery Script - No Korean Characters

Write-Host "🚨 AIRISS EMERGENCY RECOVERY STARTED" -ForegroundColor Red
Write-Host "=====================================" -ForegroundColor Yellow
Write-Host ""

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "Start Time: $timestamp" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Error Logs
Write-Host "Step 1: Checking Error Logs" -ForegroundColor Green
Write-Host "----------------------------" -ForegroundColor Gray

try {
    $errorLogs = eb logs --all | Select-String -Pattern "ERROR|FAIL|Exception|failed" | Select-Object -Last 10
    if ($errorLogs) {
        Write-Host "Found Errors:" -ForegroundColor Red
        $errorLogs | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    } else {
        Write-Host "No clear error logs found." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error checking logs: $_" -ForegroundColor Red
}

Write-Host ""

# Step 2: Backup Current Application
Write-Host "Step 2: Backup Current Application" -ForegroundColor Green
Write-Host "-----------------------------------" -ForegroundColor Gray

$backupTime = Get-Date -Format "yyyyMMdd_HHmmss"
try {
    Copy-Item "application.py" "application_backup_$backupTime.py" -Force
    Write-Host "✅ Backup completed: application_backup_$backupTime.py" -ForegroundColor Green
} catch {
    Write-Host "❌ Backup failed: $_" -ForegroundColor Red
}

# Step 3: Deploy Emergency Version
Write-Host "Step 3: Deploy Emergency Version" -ForegroundColor Green
Write-Host "---------------------------------" -ForegroundColor Gray

try {
    Copy-Item "application_emergency.py" "application.py" -Force
    Write-Host "✅ Emergency version activated" -ForegroundColor Green
    
    Write-Host "🚀 Starting emergency deployment..." -ForegroundColor Cyan
    eb deploy --timeout=15
    
    Write-Host "⏳ Waiting for deployment completion (60 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    
} catch {
    Write-Host "❌ Emergency deployment failed: $_" -ForegroundColor Red
    
    Write-Host "🔄 Trying environment restart..." -ForegroundColor Yellow
    try {
        eb restart
        Start-Sleep -Seconds 30
        Write-Host "✅ Environment restart completed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Environment restart also failed: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Step 4: Check Recovery Status
Write-Host "Step 4: Check Recovery Status" -ForegroundColor Green
Write-Host "------------------------------" -ForegroundColor Gray

try {
    Write-Host "Checking health status..." -ForegroundColor Yellow
    eb health --refresh
    
    Write-Host "Checking overall status..." -ForegroundColor Yellow
    eb status
    
} catch {
    Write-Host "Error checking status: $_" -ForegroundColor Red
}

Write-Host ""

# Step 5: Test Endpoints
Write-Host "Step 5: Test Endpoints" -ForegroundColor Green
Write-Host "----------------------" -ForegroundColor Gray

$url = "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com"

try {
    Write-Host "Testing root endpoint..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/" -TimeoutSec 10
    Write-Host "✅ Root: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root endpoint failed: $_" -ForegroundColor Red
}

try {
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 10
    Write-Host "✅ Health: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health endpoint failed: $_" -ForegroundColor Red
}

Write-Host ""

# Final Result
Write-Host "🏁 EMERGENCY RECOVERY COMPLETED!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow

$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "End Time: $endTime" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Check if Health changed to Green" -ForegroundColor White
Write-Host "2. If still Red, complete environment rebuild needed" -ForegroundColor White
Write-Host "3. After recovery, restore original application.py" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to continue..."
