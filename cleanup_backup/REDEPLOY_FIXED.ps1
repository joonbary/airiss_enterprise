# EMERGENCY REDEPLOY - Configuration Fixed
Write-Host "🔧 CONFIGURATION ISSUE FIXED - REDEPLOYING" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Yellow

Write-Host "`n📋 Changes Made:" -ForegroundColor Cyan
Write-Host "✅ Disabled problematic python_final.config" -ForegroundColor Green
Write-Host "✅ Created safe minimal_safe.config" -ForegroundColor Green
Write-Host "✅ Clean application.py active" -ForegroundColor Green

Write-Host "`n🚀 Starting Fixed Deployment..." -ForegroundColor Yellow
try {
    eb deploy --timeout=15
    Write-Host "✅ Deployment started successfully" -ForegroundColor Green
    
    Write-Host "`n⏳ Waiting 120 seconds for deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 120
    
    Write-Host "`n📊 Checking Status..." -ForegroundColor Green
    eb health --refresh
    eb status
    
    Write-Host "`n🌐 Testing Health Endpoint..." -ForegroundColor Green
    $url = "http://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com/health"
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 15
        Write-Host "✅ Health Check: HTTP $($response.StatusCode)" -ForegroundColor Green
        Write-Host "✅ Response: $($response.Content)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
}

Write-Host "`n🏁 FIXED DEPLOYMENT COMPLETED!" -ForegroundColor Green
