# AIRISS v4 Project Cleanup - PowerShell Version
# Encoding: UTF-8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎯 AIRISS v4 Project Cleanup Script" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will:" -ForegroundColor Green
Write-Host "✅ Create full backup (safety first)" -ForegroundColor White
Write-Host "🧹 Clean up unnecessary files" -ForegroundColor White
Write-Host "📦 Move files to cleanup_backup folder" -ForegroundColor White
Write-Host "📋 Generate clean structure summary" -ForegroundColor White
Write-Host ""

Write-Host "Core structure after cleanup:" -ForegroundColor Yellow
Write-Host "├── app/                 (Backend API)" -ForegroundColor White
Write-Host "├── airiss-v4-frontend/  (React Frontend)" -ForegroundColor White
Write-Host "├── requirements.txt     (Dependencies)" -ForegroundColor White
Write-Host "├── README.md           (Documentation)" -ForegroundColor White
Write-Host "├── Dockerfile          (Container)" -ForegroundColor White
Write-Host "└── .env.example        (Environment config)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Do you want to proceed with cleanup? (y/N)"

if ($choice -eq "y" -or $choice -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting cleanup..." -ForegroundColor Green
    
    try {
        python cleanup_airiss_v4.py
        Write-Host ""
        Write-Host "✅ Cleanup completed!" -ForegroundColor Green
        Write-Host "📋 Check PROJECT_STRUCTURE_CLEAN.md for results." -ForegroundColor Cyan
        Write-Host "📦 Check backup folders for archived files." -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ Error during cleanup: $_" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "❌ Cleanup cancelled." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
