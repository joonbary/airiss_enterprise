@echo off
chcp 65001 >nul
title AIRISS Quick Deploy Package Creator

echo ================================================
echo AIRISS Quick Deploy Package Creator
echo ================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Step 1: Clean old deployment files...
if exist "airiss_quick_deploy.zip" del "airiss_quick_deploy.zip"
if exist "temp_deploy" rmdir /s /q "temp_deploy"

echo Step 2: Create deployment folder...
mkdir temp_deploy
mkdir temp_deploy\app
mkdir temp_deploy\app\services
mkdir temp_deploy\app\db
mkdir temp_deploy\app\templates
mkdir temp_deploy\app\static

echo Step 3: Copy essential files...
copy "application_phase2_preparation.py" "temp_deploy\application.py"
copy "requirements.txt" "temp_deploy\"
copy "Procfile" "temp_deploy\"
copy ".ebextensions\*" "temp_deploy\.ebextensions\" 2>nul

xcopy "app\services\*.py" "temp_deploy\app\services\" /y
xcopy "app\db\*.py" "temp_deploy\app\db\" /y
xcopy "app\templates\*" "temp_deploy\app\templates\" /y /s
xcopy "app\static\*" "temp_deploy\app\static\" /y /s

echo Step 4: Create zip package...
cd temp_deploy
powershell -command "Compress-Archive -Path * -DestinationPath ..\airiss_quick_deploy.zip -Force"
cd ..

echo Step 5: Cleanup...
rmdir /s /q "temp_deploy"

echo.
echo ================================================
echo Package created: airiss_quick_deploy.zip
echo File size:
dir "airiss_quick_deploy.zip"
echo.
echo Ready for AWS upload!
echo ================================================
pause
