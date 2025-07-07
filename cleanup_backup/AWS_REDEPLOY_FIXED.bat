@echo off
chcp 65001 >nul
title AIRISS AWS Redeploy - Fixed Version

echo ================================================
echo AIRISS AWS Elastic Beanstalk Redeploy
echo ================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
echo Current Directory: %CD%
echo.

echo Step 1: Create deployment package...
if exist "airiss_fixed_deployment.zip" del "airiss_fixed_deployment.zip"

echo Step 2: Creating zip package...
powershell -command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; $source = Get-Location; $destination = Join-Path $source 'airiss_fixed_deployment.zip'; [System.IO.Compression.ZipFile]::CreateFromDirectory($source, $destination, 'Optimal', $false); Get-ChildItem $destination}"

echo.
echo Step 3: Check AWS CLI...
aws --version
if %errorlevel% neq 0 (
    echo AWS CLI not found. Please install AWS CLI first.
    echo Download: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

echo.
echo Step 4: Deploy to AWS Elastic Beanstalk...
echo Application: airiss-v4
echo Environment: airiss-v4-env
echo.

eb deploy --timeout 20

echo.
echo Step 5: Check deployment status...
eb status

echo.
echo Step 6: Open application in browser...
eb open

echo.
echo ================================================
echo Deployment completed!
echo Check your application status above.
echo ================================================
pause
