@echo off
chcp 65001 >nul
echo ============================================================
echo AIRISS v4 Project Cleanup Script (Permission Error Fixed)
echo ============================================================
echo.
echo This FIXED script will:
echo [+] Create full backup (excluding venv, node_modules)
echo [+] Clean up unnecessary files safely
echo [+] Skip protected folders (venv, .git, node_modules)
echo [+] Handle permission errors gracefully
echo.
echo Protected folders (will NOT be touched):
echo - venv/          (Python virtual environment)
echo - node_modules/  (Node.js modules)
echo - .git/          (Git repository)
echo - app/           (Core backend)
echo - airiss-v4-frontend/ (Core frontend)
echo.
set /p choice="Run SAFE cleanup? (y/N): "

if /i "%choice%"=="y" (
    echo.
    echo Starting SAFE cleanup...
    python cleanup_airiss_v4_fixed.py
    echo.
    echo SAFE cleanup completed!
) else (
    echo.
    echo Cleanup cancelled.
)

echo.
pause
