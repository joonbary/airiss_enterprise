@echo off
echo AWS Deploy Starting...

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Current directory: %CD%

echo Checking AWS CLI...
aws --version
if %ERRORLEVEL% NEQ 0 (
    echo AWS CLI not found
    pause
    exit /b 1
)

echo Creating deployment package...
if exist "application.zip" del application.zip

echo Copying main application file...
copy application_phase2_preparation.py application.py

echo Updating Procfile...
echo web: python application.py > Procfile

echo Creating ZIP package...
python create_deployment_zip.py

echo Deploying to AWS...
eb deploy --timeout 20

echo Checking status...
eb status

echo Deploy complete!
pause