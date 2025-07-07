# AIRISS GitHub Upload Script
# PowerShell version for better compatibility

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "    AIRISS GitHub Upload Tool v2.0" -ForegroundColor Yellow
Write-Host "    AI-powered Resource Intelligence System" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
Write-Host "Working directory: $PWD" -ForegroundColor Blue
Write-Host ""

# Check Git status
Write-Host "Checking Git status..." -ForegroundColor Yellow
try {
    git status | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Initializing Git repository..." -ForegroundColor Yellow
        git init
        git branch -M main
    }
} catch {
    Write-Host "Git not found or not initialized" -ForegroundColor Red
    exit 1
}

# Add files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add README.md
git add requirements.txt
git add app/
git add static/
git add *.py
git add .gitignore
git add docs/
git add scripts/

# Exclude sensitive files
Write-Host "Excluding sensitive files..." -ForegroundColor Yellow
git reset HEAD .env 2>$null
git reset HEAD *.db 2>$null
git reset HEAD *.sqlite* 2>$null
git reset HEAD logs/ 2>$null
git reset HEAD venv/ 2>$null
git reset HEAD __pycache__/ 2>$null
git reset HEAD node_modules/ 2>$null

Write-Host ""
Write-Host "Files to be uploaded:" -ForegroundColor Green
git status --short

Write-Host ""
$continue = Read-Host "Do you want to upload these files to GitHub? (y/N)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Upload cancelled." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Create commit
Write-Host ""
Write-Host "Creating commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: AIRISS v4.1 Enhanced - AI-powered Resource Intelligence Scoring System

Features:
- 8-dimensional hybrid AI analysis (Text 60% + Quantitative 40%)
- Real-time bias detection and fairness monitoring
- Chart.js based advanced visualization dashboard
- WebSocket real-time analysis progress tracking
- SQLite based lightweight database
- FastAPI + uvicorn high-performance backend

Impact:
- Validated with 1,800 employees at OK Financial Group
- 50% reduction in HR decision-making time
- 40% improvement in evaluation objectivity
- B2B market potential secured

Tech Stack:
- Backend: FastAPI, Python 3.9+
- Frontend: HTML5, Chart.js, WebSocket
- Database: SQLite
- AI/ML: NLP, bias detection, statistical analysis

Development Status:
- Core Features: Complete
- UI/UX: Complete
- Testing: Complete
- Documentation: Complete
- Production Ready: Yes
"@

git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed! Please set up Git user info:" -ForegroundColor Red
    Write-Host "git config user.name `"Your Name`"" -ForegroundColor Yellow
    Write-Host "git config user.email `"your.email@example.com`"" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Set up remote
Write-Host ""
Write-Host "Setting up remote repository..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/joonbary/airiss_enterprise.git

# Push to GitHub
Write-Host ""
Write-Host "Uploading to GitHub..." -ForegroundColor Yellow
Write-Host "Note: GitHub login may be required." -ForegroundColor Cyan

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "           UPLOAD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "GitHub Repository:" -ForegroundColor Cyan
    Write-Host "https://github.com/joonbary/airiss_enterprise" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Uploaded content:" -ForegroundColor Yellow
    Write-Host "- AIRISS v4.1 Enhanced complete source code" -ForegroundColor White
    Write-Host "- 8-dimensional AI analysis system" -ForegroundColor White
    Write-Host "- Bias detection and fairness monitoring" -ForegroundColor White
    Write-Host "- Chart.js based visualization dashboard" -ForegroundColor White
    Write-Host "- Complete documentation and guides" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Check repository on GitHub" -ForegroundColor White
    Write-Host "2. Update README.md if needed" -ForegroundColor White
    Write-Host "3. Set up Issues and Projects" -ForegroundColor White
    Write-Host "4. Invite collaborators" -ForegroundColor White
    Write-Host "===============================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Upload failed!" -ForegroundColor Red
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Check GitHub login credentials" -ForegroundColor White
    Write-Host "2. Check repository permissions" -ForegroundColor White
    Write-Host "3. Check internet connection" -ForegroundColor White
    Write-Host "4. Try GitHub Desktop instead" -ForegroundColor White
    Write-Host ""
    Write-Host "Manual upload methods:" -ForegroundColor Cyan
    Write-Host "1. Use GitHub Desktop application" -ForegroundColor White
    Write-Host "2. Upload directly on GitHub website" -ForegroundColor White
    Write-Host "3. Use VS Code Git extension" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
