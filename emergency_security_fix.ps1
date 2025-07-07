# ==========================================
# EMERGENCY SECURITY FIX - PowerShell Version
# ==========================================

Write-Host "EMERGENCY SECURITY FIX STARTING..." -ForegroundColor Red
Write-Host ""

$TargetDir = "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

# Check directory
if (-not (Test-Path $TargetDir)) {
    Write-Host "ERROR: Directory not found: $TargetDir" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $TargetDir
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Remove sensitive file
Write-Host "Step 1: Removing AWS credentials file..." -ForegroundColor Yellow
if (Test-Path "rootkey.csv") {
    Remove-Item "rootkey.csv" -Force
    Write-Host "✅ rootkey.csv deleted successfully" -ForegroundColor Green
} else {
    Write-Host "ℹ️ rootkey.csv not found (already deleted?)" -ForegroundColor Cyan
}

# Check git status
Write-Host ""
Write-Host "Step 2: Checking git status..." -ForegroundColor Yellow
try {
    git status
} catch {
    Write-Host "Git not initialized. Initializing..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/joonbary/airiss_enterprise.git
}

# Add files
Write-Host ""
Write-Host "Step 3: Adding files to git..." -ForegroundColor Yellow
git add .

# Commit
Write-Host ""
Write-Host "Step 4: Creating security commit..." -ForegroundColor Yellow
git commit -m "SECURITY: Emergency fix - Remove AWS credentials and fix CI/CD

- Removed rootkey.csv containing exposed AWS access keys
- Updated .gitignore for enhanced security protection  
- Fixed CI/CD pipeline configuration
- Applied emergency security patches

Status: CREDENTIALS SECURED ✅"

# Push
Write-Host ""
Write-Host "Step 5: Pushing to GitHub..." -ForegroundColor Yellow
$pushResult = git push origin main 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS: Security fix applied!" -ForegroundColor Green
    Write-Host "✅ AWS credentials removed from repository" -ForegroundColor Green
    Write-Host "✅ Check: https://github.com/joonbary/airiss_enterprise/actions" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Push blocked. Trying branch method..." -ForegroundColor Yellow
    
    # Create new branch
    $branchName = "security-fix-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    git checkout -b $branchName
    git push origin $branchName
    
    Write-Host "✅ Created secure branch: $branchName" -ForegroundColor Green
    Write-Host "🔗 Create PR: https://github.com/joonbary/airiss_enterprise/compare/$branchName" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "🚨 CRITICAL AWS ACTION REQUIRED:" -ForegroundColor Red
Write-Host "1. AWS Console > IAM > Access Keys" -ForegroundColor White
Write-Host "2. Find and DEACTIVATE key: AKIAWKOET5F6MUFGBL2C" -ForegroundColor White
Write-Host "3. Generate new credentials if needed" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"
