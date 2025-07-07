@echo off
chcp 65001 >nul
echo ============================================================
echo AIRISS v4 Project Cleanup Script
echo ============================================================
echo.
echo This script will:
echo [+] Create full backup (safety first)
echo [+] Clean up unnecessary files (backup/temp/duplicate files)
echo [+] Move cleaned files to cleanup_backup folder
echo [+] Generate clean project structure summary
echo.
echo Core structure after cleanup:
echo app/                 (Backend API)
echo airiss-v4-frontend/  (React Frontend)
echo requirements.txt     (Dependencies)
echo README.md           (Documentation)
echo Dockerfile          (Container)
echo .env.example        (Environment config)
echo.
echo WARNING: Full backup will be created automatically before cleanup.
echo.
set /p choice="Do you want to proceed with cleanup? (y/N): "

if /i "%choice%"=="y" (
    echo.
    echo Starting cleanup...
    python cleanup_airiss_v4.py
    echo.
    echo Cleanup completed! 
    echo Check PROJECT_STRUCTURE_CLEAN.md file for results.
    echo Check backup folders for archived files.
) else (
    echo.
    echo Cleanup cancelled.
)

echo.
pause
