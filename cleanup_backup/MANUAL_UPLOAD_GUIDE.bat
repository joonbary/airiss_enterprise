@echo off
chcp 65001 >nul
title AIRISS AWS Manual Upload Guide

echo ================================================
echo AIRISS AWS Manual Upload Process
echo ================================================
echo.

echo Step 1: Create deployment package
echo Run: CREATE_DEPLOY_PACKAGE.bat
echo This will create: airiss_quick_deploy.zip
echo.

echo Step 2: Upload to AWS Console
echo 1. Open AWS Console: https://console.aws.amazon.com
echo 2. Go to Elastic Beanstalk service
echo 3. Select your application: airiss-v4
echo 4. Click "Upload and deploy"
echo 5. Choose file: airiss_quick_deploy.zip
echo 6. Set version label: fixed-import-error
echo 7. Click "Deploy"
echo.

echo Step 3: Monitor deployment
echo - Deployment usually takes 5-10 minutes
echo - Watch for any errors in the console
echo - Check health status after deployment
echo.

echo Step 4: Test your application
echo After deployment, test these URLs:
echo - Main page: your-app-url.elasticbeanstalk.com
echo - Health: your-app-url.elasticbeanstalk.com/health
echo - Status: your-app-url.elasticbeanstalk.com/status
echo.

echo ================================================
echo Manual deployment process complete!
echo ================================================
pause
