@echo off
echo ================================================
echo 🚀 AIRISS AWS Elastic Beanstalk 즉시 재배포
echo ================================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📂 현재 디렉토리: %CD%
echo.

echo 🔧 AWS CLI 확인...
aws --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ AWS CLI가 설치되지 않았습니다.
    echo 💡 설치 링크: https://aws.amazon.com/cli/
    pause
    exit /b 1
)
echo ✅ AWS CLI OK
echo.

echo 🗂️ 기존 배포 파일 정리...
if exist "application.zip" del application.zip
if exist "temp_deployment" rmdir /s /q temp_deployment
echo.

echo 📦 배포 패키지 생성 중...
python -c "
import zipfile
import os
import shutil

# 배포용 임시 디렉토리 생성
if os.path.exists('temp_deployment'):
    shutil.rmtree('temp_deployment')
os.makedirs('temp_deployment')

# 핵심 파일들 복사
files_to_deploy = [
    'application_phase2_preparation.py',
    'requirements.txt',
    'Procfile',
    'app/',
    '.ebextensions/',
    'static/',
    'alembic.ini'
]

for item in files_to_deploy:
    if os.path.exists(item):
        if os.path.isdir(item):
            shutil.copytree(item, os.path.join('temp_deployment', item))
        else:
            shutil.copy2(item, 'temp_deployment/')

# Procfile 수정 (수정된 application 파일 사용)
with open('temp_deployment/Procfile', 'w') as f:
    f.write('web: python application_phase2_preparation.py')

# ZIP 파일 생성
with zipfile.ZipFile('application.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('temp_deployment'):
        for file in files:
            file_path = os.path.join(root, file)
            arc_path = os.path.relpath(file_path, 'temp_deployment')
            zipf.write(file_path, arc_path)

print('✅ 배포 패키지 생성 완료: application.zip')
"
echo.

echo 🌐 AWS Elastic Beanstalk 배포 시작...
eb deploy --timeout 20
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 배포 실패! 수동 배포를 시도합니다...
    echo.
    echo 🔄 수동 배포 명령어:
    echo    1. AWS 콘솔 열기: https://console.aws.amazon.com/elasticbeanstalk/
    echo    2. AIRISS 환경 선택
    echo    3. "Upload and deploy" 클릭
    echo    4. application.zip 파일 업로드
    pause
    exit /b 1
)

echo.
echo ✅ 배포 완료! 
echo.
echo 🌐 배포 상태 확인 중...
eb status
echo.

echo 📊 애플리케이션 URL 확인...
for /f "tokens=2 delims= " %%i in ('eb status ^| findstr "CNAME"') do set APP_URL=%%i
echo.
echo 🎉 배포 완료!
echo 🌐 애플리케이션 URL: http://%APP_URL%
echo 📊 상태 확인: http://%APP_URL%/status
echo 🏥 헬스체크: http://%APP_URL%/health
echo.

echo 🔍 즉시 테스트 중...
timeout /t 30 /nobreak
curl -s http://%APP_URL%/health
echo.

echo ================================================
echo 🎊 AWS 재배포 완료!
echo ================================================
pause