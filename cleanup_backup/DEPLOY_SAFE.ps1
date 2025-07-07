# AIRISS AWS Deployment Script - PowerShell Safe Mode
Write-Host "===========================================" -ForegroundColor Green
Write-Host "AIRISS AWS Deploy - PowerShell Safe Mode" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

# Change to project directory
Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

Write-Host "Step 1: Deploying to AWS..." -ForegroundColor Yellow
eb deploy

Write-Host "Step 2: Checking deployment status..." -ForegroundColor Yellow
eb status

Write-Host "Step 3: Opening in browser..." -ForegroundColor Yellow
eb open

Write-Host "===========================================" -ForegroundColor Green
Write-Host "Deployment completed! Check your browser." -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

Read-Host "Press Enter to continue"
