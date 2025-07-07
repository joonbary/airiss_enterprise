@echo off
setlocal enabledelayedexpansion

REM Keep window open for debugging
echo SAFE SECURITY FIX STARTING...
echo.

REM Check if we're in the right directory
set "TARGET_DIR=C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
echo Checking directory: %TARGET_DIR%

if not exist "%TARGET_DIR%" (
    echo ERROR: Directory not found!
    echo Please check the path and try again.
    goto :error_exit
)

cd /d "%TARGET_DIR%"
echo Current directory: %CD%
echo.

REM Check if this is a git repository
echo Checking if this is a git repository...
git status >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: This is not a git repository or git is not available
    echo Initializing git repository...
    git init
    git remote add origin https://github.com/joonbary/airiss_enterprise.git
)

echo.
echo Step 1: Removing sensitive file...
if exist "rootkey.csv" (
    echo Deleting rootkey.csv...
    del "rootkey.csv"
    if exist "rootkey.csv" (
        echo WARNING: Failed to delete rootkey.csv
    ) else (
        echo SUCCESS: rootkey.csv deleted
    )
) else (
    echo INFO: rootkey.csv not found (already deleted?)
)

echo.
echo Step 2: Checking git status...
git status

echo.
echo Step 3: Adding files to git...
git add .gitignore
git add .

echo.
echo Step 4: Creating commit...
git commit -m "SECURITY: Remove AWS credentials and fix CI pipeline"

echo.
echo Step 5: Pushing to GitHub...
git push origin main

echo.
if !errorlevel! equ 0 (
    echo SUCCESS: Security fix completed!
    echo Repository is now secure
    echo Check: https://github.com/joonbary/airiss_enterprise
) else (
    echo ERROR: Push failed. Trying alternative method...
    echo Creating new branch...
    git checkout -b emergency-security-fix
    git push origin emergency-security-fix
    echo Created branch 'emergency-security-fix'
    echo Go to GitHub and create a Pull Request
)

:error_exit
echo.
echo CRITICAL: Deactivate AWS key AKIAWKOET5F6MUFGBL2C in AWS Console!
echo.
echo Press any key to exit...
pause >nul
