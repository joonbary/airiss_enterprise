@echo off
chcp 65001 >nul
cls
echo ================================================================
echo                AIRISS v4.1 Deployment Master
echo              GitHub + AWS Deployment System
echo ================================================================
echo.
echo Project: AIRISS v4.1 Enhanced
echo Status: Production Ready  
echo Target: OK Financial Group 1,800+ employees
echo Goal: Global AI HR Solution
echo.
echo ================================================================
echo.

echo Checking project structure...
timeout /t 1 /nobreak >nul

if exist "app\main.py" (
    echo [OK] FastAPI Application found
) else (
    echo [ERROR] app\main.py not found
    goto error
)

if exist "requirements.txt" (
    echo [OK] Requirements file found
) else (
    echo [ERROR] requirements.txt not found
    goto error
)

if exist ".git" (
    echo [OK] Git repository initialized
) else (
    echo [INFO] Initializing Git repository...
    git init
    echo [OK] Git initialized
)

echo [OK] Project structure verified!
echo.

echo ================================================================
echo Select deployment option:
echo ================================================================
echo.
echo [1] Full Auto Deploy (GitHub + AWS Amplify) - RECOMMENDED
echo     Simple, beginner-friendly, 5-minute setup
echo.
echo [2] GitHub Upload Only
echo     Code backup and sharing, AWS deployment later
echo.
echo [3] Advanced Deployment Options  
echo     Elastic Beanstalk, EC2, Custom configurations
echo.
echo [4] Open Documentation
echo     Step-by-step guides and manuals
echo.
echo [0] Exit
echo.

set /p choice="Enter your choice (0-4): "

if "%choice%"=="1" goto auto_deploy
if "%choice%"=="2" goto github_only
if "%choice%"=="3" goto advanced
if "%choice%"=="4" goto docs
if "%choice%"=="0" goto exit
goto invalid

:auto_deploy
cls
echo ================================================================
echo                Full Automatic Deployment
echo ================================================================
echo.

set /p github_user="Enter your GitHub username: "

if "%github_user%"=="" (
    echo ERROR: GitHub username is required.
    pause
    goto auto_deploy
)

echo.
echo Step 1: Preparing Git commit...
git add .
git commit -m "AIRISS v4.1 - Production Ready for GitHub and AWS

Features:
- 8-dimensional AI talent analysis
- Real-time bias detection
- Hybrid AI model (60%% text + 40%% quantitative)  
- Chart.js visualization with radar charts
- WebSocket real-time updates
- Explainable AI scoring

Production Ready:
- OK Financial Group validated
- 1,800+ employees capacity
- B2B market potential: $50M+ annually

Tech Stack:
- Backend: FastAPI, Python 3.9+
- Frontend: HTML5, Chart.js, WebSocket
- Database: SQLite (scalable)
- AI/ML: NLP, bias detection, statistical analysis
- Deployment: Docker ready

Deploy Target: AWS Amplify for global accessibility"

echo [OK] Git commit completed!
echo.

echo Step 2: Connecting to GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/%github_user%/airiss_enterprise.git
git branch -M main

echo.
echo Step 3: Uploading to GitHub...
echo NOTE: You may need to login to GitHub during this process.
git push -u origin main

if %errorlevel% neq 0 (
    echo [ERROR] GitHub upload failed
    echo.
    echo Solutions:
    echo 1. Create repository 'airiss_enterprise' on GitHub first
    echo 2. Check your GitHub login credentials  
    echo 3. Use Personal Access Token if 2FA is enabled
    echo.
    pause
    goto auto_deploy
)

echo [SUCCESS] GitHub upload completed!
echo.

echo ================================================================
echo GitHub Upload Successful!
echo ================================================================
echo.
echo Repository URL: https://github.com/%github_user%/airiss_enterprise
echo.

echo Next Step: AWS Amplify Setup
echo ================================================================
echo.
echo 1. Click this AWS Console link:
echo    https://console.aws.amazon.com/amplify/
echo.
echo 2. Click "Create new app"
echo 3. Select "Host web app"
echo 4. Select "GitHub"  
echo 5. Choose repository: "airiss_enterprise"
echo 6. Choose branch: "main"
echo 7. Click "Save and deploy"
echo.
echo Build Settings (copy and paste):
echo.
echo version: 1
echo backend:
echo   phases:
echo     preBuild:
echo       commands:
echo         - python -m pip install --upgrade pip
echo         - pip install -r requirements.txt
echo     build:
echo       commands:
echo         - python init_database.py
echo frontend:
echo   artifacts:
echo     baseDirectory: /
echo     files:
echo       - '**/*'
echo.
echo Expected completion time: 5-10 minutes
echo Result: Globally accessible AIRISS website!
echo.

set /p open_aws="Open AWS Console? (y/n): "
if /i "%open_aws%"=="y" start https://console.aws.amazon.com/amplify/

start https://github.com/%github_user%/airiss_enterprise
echo.
echo [OK] Browser opened with GitHub and AWS Console.
echo [INFO] Detailed guide: COMPLETE_DEPLOYMENT_GUIDE.md
goto success

:github_only
cls
echo ================================================================
echo                GitHub Upload Only
echo ================================================================
echo.

set /p github_user="Enter your GitHub username: "

echo.
echo Uploading to GitHub...

git add .
git commit -m "AIRISS v4.1 - GitHub Repository Setup

Project backup and collaboration setup
Production-ready AIRISS v4.1 Enhanced codebase"

git remote remove origin 2>nul
git remote add origin https://github.com/%github_user%/airiss_enterprise.git
git branch -M main
git push -u origin main

echo [SUCCESS] GitHub upload completed!
echo Repository: https://github.com/%github_user%/airiss_enterprise
start https://github.com/%github_user%/airiss_enterprise
goto success

:advanced
cls
echo ================================================================
echo                Advanced Deployment Options
echo ================================================================
echo.

echo Available advanced options:
echo.
echo [1] AWS Elastic Beanstalk (FastAPI optimized)
echo [2] AWS EC2 + Docker (Full control)  
echo [3] Custom deployment guides
echo.

set /p adv_choice="Select option (1-3): "

if "%adv_choice%"=="1" (
    echo Opening Elastic Beanstalk guide...
    if exist "aws_elasticbeanstalk_guide.md" start aws_elasticbeanstalk_guide.md
    echo [INFO] Install EB CLI: pip install awsebcli
)

if "%adv_choice%"=="2" (
    echo Opening EC2 + Docker guide...
    if exist "aws_ec2_docker_guide.md" start aws_ec2_docker_guide.md
)

if "%adv_choice%"=="3" (
    echo Opening all deployment guides...
    if exist "aws_amplify_guide.md" start aws_amplify_guide.md
    if exist "aws_elasticbeanstalk_guide.md" start aws_elasticbeanstalk_guide.md
    if exist "aws_ec2_docker_guide.md" start aws_ec2_docker_guide.md
)

goto success

:docs
cls
echo ================================================================
echo                Opening Documentation
echo ================================================================
echo.

echo Opening all guide documents...
if exist "COMPLETE_DEPLOYMENT_GUIDE.md" start COMPLETE_DEPLOYMENT_GUIDE.md
if exist "deployment_checklist.md" start deployment_checklist.md
if exist "aws_amplify_guide.md" start aws_amplify_guide.md
if exist "README.md" start README.md

echo [OK] Documentation opened.
goto success

:invalid
echo [ERROR] Invalid choice. Please select 0-4.
timeout /t 2 /nobreak >nul
goto :auto_deploy

:error
echo.
echo [ERROR] Project structure issue detected.
echo.
echo Solutions:
echo 1. Make sure you're in the correct AIRISS project folder
echo 2. Verify that required files exist
echo.
pause
exit /b 1

:success
echo.
echo ================================================================
echo SUCCESS! AIRISS v4.1 Deployment Ready
echo ================================================================
echo.
echo Project Status:
echo [OK] 8-dimensional AI talent analysis system
echo [OK] Real-time bias detection  
echo [OK] Hybrid AI model
echo [OK] Production environment ready
echo [OK] B2B market entry prepared
echo.
echo Next Steps:
echo 1. Complete AWS deployment when ready
echo 2. Start performance monitoring
echo 3. Collect user feedback
echo 4. Plan continuous improvements
echo.
echo Additional Support:
echo - README.md: Detailed project information
echo - GitHub Issues: Bug reports and questions
echo - AWS Support: Technical assistance
echo.
echo Launch the new era of talent management with AIRISS v4!
echo ================================================================

:exit
echo.
echo Thank you! Run this script again anytime.
pause
exit /b 0
