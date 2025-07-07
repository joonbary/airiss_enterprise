# IMMEDIATE EMERGENCY DEPLOYMENT
# Run this script to deploy the clean emergency version

Write-Host "🚨 EMERGENCY DEPLOYMENT STARTING..." -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "Deployment Start Time: $timestamp" -ForegroundColor Cyan

# Check current files
Write-Host "`n📁 Checking Files..." -ForegroundColor Green
if (Test-Path "application.py") {
    Write-Host "✅ application.py exists" -ForegroundColor Green
} else {
    Write-Host "❌ application.py missing!" -ForegroundColor Red
    exit 1
}

if (Test-Path "Procfile") {
    Write-Host "✅ Procfile exists" -ForegroundColor Green
} else {
    Write-Host "❌ Procfile missing!" -ForegroundColor Red
    exit 1
}

# Deploy immediately
Write-Host "`n🚀 Starting Emergency Deployment..." -ForegroundColor Yellow
Write-Host "Command: eb deploy --timeout=15" -ForegroundColor Gray

try {
    eb deploy --timeout=15
    Write-Host "✅ Deployment command executed" -ForegroundColor Green
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    
    Write-Host "`n🔄 Trying environment restart as fallback..." -ForegroundColor Yellow
    try {
        eb restart
        Write-Host "✅ Environment restart executed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Environment restart also failed: $_" -ForegroundColor Red
    }
}

# Wait for deployment
Write-Host "`n⏳ Waiting 90 seconds for deployment to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 90

# Check status
Write-Host "`n📊 Checking Status..." -ForegroundColor Green
try {
    eb health --refresh
    eb status
} catch {
    Write-Host "Error checking status: $_" -ForegroundColor Red
}

# Test endpoints
Write-Host "`n🌐 Testing Endpoints..." -ForegroundColor Green
$url = "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com"

# Test health endpoint
try {
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/health" -TimeoutSec 10
    Write-Host "✅ Health: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health failed: $_" -ForegroundColor Red
}

# Test root endpoint
try {
    Write-Host "Testing root endpoint..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "$url/" -TimeoutSec 10
    Write-Host "✅ Root: HTTP $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root failed: $_" -ForegroundColor Red
}

Write-Host "`n🏁 EMERGENCY DEPLOYMENT COMPLETED!" -ForegroundColor Green
$endTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "End Time: $endTime" -ForegroundColor Cyan

Write-Host "`nNext: Monitor AWS EB console for Health status change to Green" -ForegroundColor Cyan
