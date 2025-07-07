# ==========================================
# AIRISS Emergency CI Fix - PowerShell Script
# ==========================================

Write-Host "AIRISS Emergency CI Fix Starting..." -ForegroundColor Green

Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

Write-Host "Checking git status..." -ForegroundColor Cyan
git status

Write-Host "Adding all changes..." -ForegroundColor Cyan
git add .

Write-Host "Creating commit..." -ForegroundColor Cyan
git commit -m "Emergency CI/CD Fix - Simplified pipeline for immediate deployment"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Changes pushed to GitHub!" -ForegroundColor Green
    Write-Host "CI/CD pipeline should now pass" -ForegroundColor Green
    Write-Host "Check: https://github.com/joonbary/airiss_enterprise/actions" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Push failed. Check git configuration." -ForegroundColor Red
    Write-Host "Try: git remote -v" -ForegroundColor Yellow
    Write-Host "Try: git branch -a" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Magenta
Write-Host "1. Check GitHub Actions in 2 minutes"
Write-Host "2. Verify CI pipeline passes"
Write-Host "3. Resume deployment process"

Read-Host "Press Enter to continue"
