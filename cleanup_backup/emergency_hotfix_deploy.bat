@echo off
echo.
echo 🚨 AIRISS v4 긴급 수정 배포
echo ========================
echo.
echo 문제: /health 엔드포인트 연결 시간 초과
echo 해결: 안정화된 application.py로 교체 후 재배포
echo.

echo 1️⃣ 현재 application.py 백업 중...
if exist application.py (
    copy application.py application_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.py >nul
    echo ✅ 백업 완료: application_backup_*.py
) else (
    echo ❌ application.py 파일이 없습니다.
    pause
    exit /b 1
)

echo.
echo 2️⃣ 안정화된 버전으로 교체 중...
if exist application_stable.py (
    copy application_stable.py application.py >nul
    echo ✅ 안정화된 application.py로 교체 완료
) else (
    echo ❌ application_stable.py 파일이 없습니다.
    pause
    exit /b 1
)

echo.
echo 3️⃣ 긴급 배포 패키지 생성 중...

python -c "
import zipfile
import os
from datetime import datetime

timestamp = datetime.now().strftime('%%Y%%m%%d_%%H%%M%%S')
zip_name = f'airiss_v4_hotfix_{timestamp}.zip'

# 필수 파일들만 포함
essential_files = [
    'application.py',
    'Procfile',
    'requirements.txt',
    'runtime.txt'
]

# .ebextensions 디렉토리 포함
eb_files = []
if os.path.exists('.ebextensions'):
    for root, dirs, files in os.walk('.ebextensions'):
        for file in files:
            eb_files.append(os.path.join(root, file))

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 필수 파일들 추가
    for file in essential_files:
        if os.path.exists(file):
            zipf.write(file)
            print(f'Added: {file}')
        else:
            print(f'Warning: {file} not found')
    
    # EB 설정 파일들 추가
    for file in eb_files:
        zipf.write(file)
        print(f'Added: {file}')

print(f'\\n✅ 긴급 배포 패키지 생성: {zip_name}')
print(f'📦 파일 경로: {os.path.abspath(zip_name)}')
"

echo.
echo 4️⃣ 배포 상태 확인 스크립트 생성...

(
echo import requests
echo import time
echo.
echo def check_deployment^(^):
echo     url = "https://airiss-v4.ap-northeast-2.elasticbeanstalk.com"
echo     endpoints = ["/", "/health", "/api", "/status"]
echo     
echo     print^("🔍 배포 후 상태 확인 중..."^)
echo     print^("=" * 50^)
echo     
echo     for endpoint in endpoints:
echo         try:
echo             response = requests.get^(f"{url}{endpoint}", timeout=10^)
echo             if response.status_code == 200:
echo                 print^(f"✅ {endpoint}: OK"^)
echo             else:
echo                 print^(f"❌ {endpoint}: HTTP {response.status_code}"^)
echo         except:
echo             print^(f"❌ {endpoint}: Connection failed"^)
echo.
echo if __name__ == "__main__":
echo     check_deployment^(^)
) > check_deployment_status.py

echo ✅ 상태 확인 스크립트 생성: check_deployment_status.py

echo.
echo 🎉 긴급 수정 준비 완료!
echo.
echo 📋 다음 단계:
echo 1. AWS Elastic Beanstalk 콘솔 접속
echo 2. 환경: AIRISS-v4-Production-env-1 선택
echo 3. "새 버전 업로드 및 배포" 클릭
echo 4. 생성된 airiss_v4_hotfix_*.zip 파일 업로드
echo 5. 배포 완료 후 check_deployment_status.py 실행
echo.
echo 🔗 AWS 콘솔: https://console.aws.amazon.com/elasticbeanstalk/
echo.
echo ⏱️ 예상 배포 시간: 3-5분
echo 📊 수정된 기능: 안정화된 모든 엔드포인트 (/health 포함)
echo.
pause
