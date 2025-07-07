# AIRISS Phase 2 Core Services Test (PowerShell)
# UTF-8 encoding safe version

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIRISS Phase 2 Core Services Test" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Change to project directory
$projectPath = "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
Set-Location $projectPath

Write-Host ""
Write-Host "[1/5] Checking Python environment..." -ForegroundColor Green

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "Virtual environment found. Activating..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\activate.bat") {
    Write-Host "Virtual environment found. Activating (batch mode)..." -ForegroundColor Green
    cmd /c "venv\Scripts\activate.bat"
} else {
    Write-Host "Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
    } else {
        Write-Host "Installing basic FastAPI dependencies..." -ForegroundColor Yellow
        pip install fastapi uvicorn jinja2 python-multipart
    }
}

Write-Host ""
Write-Host "[3/5] Checking Phase 2 application file..." -ForegroundColor Green

if (Test-Path "application_phase2_preparation.py") {
    Write-Host "Phase 2 application file found!" -ForegroundColor Green
} else {
    Write-Host "ERROR: application_phase2_preparation.py not found!" -ForegroundColor Red
    Write-Host "Please ensure the file exists in the current directory." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[4/5] Starting Phase 2 server..." -ForegroundColor Green
Write-Host "Server URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Status Check: http://localhost:8000/status" -ForegroundColor Cyan
Write-Host "DB Health: http://localhost:8000/health/db" -ForegroundColor Cyan
Write-Host "AI Health: http://localhost:8000/health/analysis" -ForegroundColor Cyan
Write-Host ""

# Start the server
try {
    Write-Host "Starting server... (Press Ctrl+C to stop)" -ForegroundColor Yellow
    python application_phase2_preparation.py
} catch {
    Write-Host "ERROR: Failed to start server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/5] Test completed!" -ForegroundColor Green
Write-Host "Open browser and go to http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue..."
