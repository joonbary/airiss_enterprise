@echo off
echo.
echo 🚀 AIRISS v4.1 전체 기능 업그레이드 도구
echo ========================================
echo.

echo 📋 현재 상태: 최소 버전 배포 완료
echo 🎯 목표: 전체 기능 활성화
echo.

echo 1️⃣ 백업 생성 중...
if exist application.py (
    copy application.py application_minimal_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py >nul
    echo ✅ 최소 버전 백업 완료
) else (
    echo ❌ application.py 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)

echo.
echo 2️⃣ 전체 버전 application.py 생성 중...

(
echo # application.py - AIRISS v4.1 Full Version
echo import os
echo import sys
echo import logging
echo from pathlib import Path
echo.
echo # 로깅 설정
echo logging.basicConfig^(level=logging.INFO^)
echo logger = logging.getLogger^(__name__^)
echo.
echo try:
echo     # 현재 디렉토리를 패스에 추가
echo     current_dir = Path^(__file__^).parent
echo     sys.path.insert^(0, str^(current_dir^)^)
echo     
echo     logger.info^("🚀 AIRISS v4.1 Full Version 시작..."^)
echo     
echo     # 메인 앱 import
echo     from app.main import app
echo     
echo     # Elastic Beanstalk 호환성
echo     application = app
echo     
echo     logger.info^("✅ AIRISS v4.1 Full Version 초기화 완료"^)
echo     
echo except Exception as e:
echo     logger.error^(f"❌ Full Version 오류: {e}"^)
echo     logger.info^("🔄 최소 모드로 폴백..."^)
echo     
echo     # 폴백: 최소 버전
echo     from fastapi import FastAPI
echo     
echo     app = FastAPI^(title="AIRISS v4.1 Fallback"^)
echo     
echo     @app.get^("/"^)
echo     async def fallback_root^(^):
echo         return {
echo             "message": "AIRISS v4.1 Fallback Mode",
echo             "status": "fallback",
echo             "error": str^(e^),
echo             "version": "4.1.0-fallback"
echo         }
echo     
echo     @app.get^("/health"^)
echo     async def fallback_health^(^):
echo         return {
echo             "status": "fallback", 
echo             "service": "AIRISS v4.1",
echo             "error": str^(e^),
echo             "mode": "minimal"
echo         }
echo     
echo     application = app
echo.
echo if __name__ == "__main__":
echo     import uvicorn
echo     uvicorn.run^(app, host="0.0.0.0", port=8000^)
) > application.py

echo ✅ 전체 버전 application.py 생성 완료

echo.
echo 3️⃣ requirements.txt 업데이트 중...

if exist requirements.txt (
    copy requirements.txt requirements_minimal_backup_%date:~0,4%%date:~5,2%%date:~8,2%.txt >nul
)

(
echo fastapi==0.104.1
echo uvicorn[standard]==0.24.0
echo gunicorn==21.2.0
echo pydantic==2.7.0
echo python-multipart==0.0.6
echo jinja2==3.1.2
echo python-dotenv==1.0.0
echo pandas==2.1.4
echo numpy==1.24.3
echo openpyxl==3.1.2
echo requests==2.31.0
echo aiofiles==23.2.0
echo websockets==12.0
echo sqlalchemy==2.0.23
echo alembic==1.13.1
echo httpx==0.25.2
echo openai==1.3.7
) > requirements.txt

echo ✅ requirements.txt 업데이트 완료

echo.
echo 4️⃣ Elastic Beanstalk 설정 최적화 중...

if not exist .ebextensions mkdir .ebextensions

(
echo option_settings:
echo   aws:elasticbeanstalk:application:environment:
echo     PYTHONPATH: "/var/app/current"
echo     ENVIRONMENT: "production"
echo     DEBUG: "false"
echo     PORT: "8000"
echo   aws:autoscaling:launchconfiguration:
echo     InstanceType: t3.medium
echo     IamInstanceProfile: aws-elasticbeanstalk-ec2-role
echo   aws:autoscaling:asg:
echo     MinSize: 1
echo     MaxSize: 1
echo   aws:elasticbeanstalk:healthreporting:system:
echo     SystemType: enhanced
echo   aws:elasticbeanstalk:application:
echo     Application Healthcheck URL: /health
echo   aws:elasticbeanstalk:command:
echo     Timeout: 300
echo   aws:elasticbeanstalk:environment:proxy:staticfiles:
echo     /static: app/static
) > .ebextensions\01_python_full.config

echo ✅ Static files 설정 추가 완료

echo.
echo 5️⃣ 배포 패키지 생성 중...

python -c "
import zipfile
import os
from datetime import datetime

timestamp = datetime.now().strftime('%%Y%%m%%d_%%H%%M%%S')
zip_name = f'airiss_v4_full_{timestamp}.zip'

exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'debug_logs', 'test_results'}
exclude_files = {'.zip', '.log', '.pyc', '.sqlite', '.db'}

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if not any(file.endswith(ext) for ext in exclude_files):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)

print(f'\\n✅ 배포 패키지 생성 완료: {zip_name}')
print(f'📦 파일 경로: {os.path.abspath(zip_name)}')
"

echo.
echo 🎉 업그레이드 준비 완료!
echo.
echo 📋 다음 단계:
echo 1. AWS Elastic Beanstalk 콘솔로 이동
echo 2. 환경: AIRISS-v4-Production-env-1 선택
echo 3. "새 버전 업로드 및 배포" 클릭
echo 4. 생성된 ZIP 파일 업로드
echo 5. 배포 완료 후 테스트
echo.
echo 🔗 AWS 콘솔: https://console.aws.amazon.com/elasticbeanstalk/
echo.
echo ⚠️ 주의사항:
echo - 배포 중에는 약 3-5분간 서비스 중단
echo - 문제 발생 시 이전 버전으로 롤백 가능
echo.
pause
