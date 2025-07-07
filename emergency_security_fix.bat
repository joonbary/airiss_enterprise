@echo off
echo ========================================================
echo 🚨 EMERGENCY SECURITY FIX - AWS KEYS CLEANUP 🚨
echo ========================================================
echo.

echo ⚠️  WARNING: This script will permanently remove AWS keys from Git history
echo    This action cannot be undone!
echo.
pause

echo 📍 Step 1: Backing up current state...
git status > backup_git_status.txt
git log --oneline -10 > backup_git_log.txt

echo 📍 Step 2: Removing sensitive file from working directory...
if exist "rootkey.csv" (
    del /f "rootkey.csv"
    echo ✅ rootkey.csv deleted from working directory
) else (
    echo ℹ️  rootkey.csv not found in working directory
)

echo 📍 Step 3: Adding to .gitignore...
echo. >> .gitignore
echo # Security - Never commit these files >> .gitignore
echo rootkey.csv >> .gitignore
echo *.csv >> .gitignore
echo .env >> .gitignore
echo .env.local >> .gitignore
echo *.key >> .gitignore
echo *.pem >> .gitignore
echo credentials.json >> .gitignore
echo config.ini >> .gitignore

echo 📍 Step 4: Removing from Git index...
git rm --cached rootkey.csv 2>nul
git add .gitignore

echo 📍 Step 5: Committing the security fix...
git commit -m "SECURITY FIX: Remove sensitive AWS credentials and update .gitignore"

echo 📍 Step 6: Removing from Git history using filter-branch...
echo ⚠️  This may take a few minutes...
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch rootkey.csv" --prune-empty --tag-name-filter cat -- --all

echo 📍 Step 7: Cleaning up refs...
git for-each-ref --format="delete %%(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo 📍 Step 8: Creating secure environment template...
echo # AIRISS AWS Configuration > .env.example
echo # Copy this file to .env and fill in your actual values >> .env.example
echo AWS_ACCESS_KEY_ID=your_access_key_here >> .env.example
echo AWS_SECRET_ACCESS_KEY=your_secret_key_here >> .env.example
echo AWS_REGION=ap-northeast-2 >> .env.example
echo AWS_S3_BUCKET=your_bucket_name >> .env.example

echo.
echo ========================================================
echo ✅ SECURITY CLEANUP COMPLETED!
echo ========================================================
echo.
echo 🔴 CRITICAL NEXT STEPS:
echo 1. Go to AWS Console immediately
echo 2. Navigate to IAM → Access Keys
echo 3. DEACTIVATE or DELETE this key: AKIAWKOET5F6MUFGBL2C
echo 4. Create new access keys if needed
echo 5. Update .env file with new credentials (never commit .env!)
echo 6. Force push to GitHub: git push origin main --force
echo.
echo 📋 AWS Console Link: https://console.aws.amazon.com/iam/home#/security_credentials
echo.
echo ⚠️  Until you deactivate the exposed key in AWS Console,
echo    your account is still at risk!
echo.
pause
