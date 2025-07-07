@echo off
echo AIRISS GitHub Upload Tool
echo ========================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
echo Current directory: %CD%
echo.

echo Checking Git status...
git status
if %errorlevel% neq 0 (
    echo Initializing Git repository...
    git init
    git branch -M main
)
echo.

echo Adding files to Git...
git add README.md
git add requirements.txt
git add app/
git add static/
git add *.py
git add .gitignore
git add docs/
git add scripts/

echo Excluding sensitive files...
git reset HEAD .env 2>nul
git reset HEAD *.db 2>nul
git reset HEAD *.sqlite* 2>nul
git reset HEAD logs/ 2>nul
git reset HEAD venv/ 2>nul
git reset HEAD __pycache__/ 2>nul

echo.
echo Files to be uploaded:
git status --short
echo.

set /p CONTINUE=Do you want to upload these files to GitHub? (y/N): 
if /i not "%CONTINUE%"=="y" (
    echo Upload cancelled.
    pause
    exit /b 1
)

echo.
echo Creating commit...
git commit -m "Initial commit: AIRISS v4.1 Enhanced - AI-powered Resource Intelligence Scoring System"

if %errorlevel% neq 0 (
    echo Commit failed! Please set up Git user info:
    echo git config user.name "Your Name"
    echo git config user.email "your.email@example.com"
    pause
    exit /b 1
)

echo.
echo Setting up remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/joonbary/airiss_enterprise.git

echo.
echo Uploading to GitHub...
git push -u origin main

if %errorlevel% eq 0 (
    echo.
    echo ================================================
    echo           UPLOAD SUCCESSFUL!
    echo ================================================
    echo.
    echo GitHub Repository:
    echo https://github.com/joonbary/airiss_enterprise
    echo.
    echo Next steps:
    echo 1. Check repository on GitHub
    echo 2. Update README.md if needed
    echo 3. Set up Issues and Projects
    echo 4. Invite collaborators
    echo ================================================
) else (
    echo.
    echo Upload failed!
    echo Possible solutions:
    echo 1. Check GitHub login
    echo 2. Check repository permissions
    echo 3. Check internet connection
    echo 4. Use GitHub Desktop instead
)

echo.
pause
