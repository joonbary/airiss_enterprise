#!/usr/bin/env python3
"""
AIRISS v4.1 연결 타임아웃 긴급 수정 스크립트
AWS Elastic Beanstalk 애플리케이션 시작 실패 문제 해결
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_fixed_application_py():
    """application.py 수정 - 포트 및 호스트 설정 보완"""
    
    content = '''# application.py - AWS Elastic Beanstalk 최적화 버전
import os
import sys
import logging
from pathlib import Path

# 현재 디렉토리를 Python 패스에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/airiss.log')
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("🚀 AIRISS v4.1 애플리케이션 시작...")
    
    # FastAPI 앱 import
    from app.main import app as fastapi_app
    
    # AWS Elastic Beanstalk용 설정
    application = fastapi_app
    app = fastapi_app  # 호환성을 위한 별칭
    
    # 환경 변수 설정
    PORT = int(os.environ.get('PORT', '8000'))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"✅ AIRISS 앱 로드 성공 - {HOST}:{PORT}")
    
    # 헬스체크 엔드포인트 강제 추가
    @fastapi_app.get("/")
    async def root():
        return {
            "message": "AIRISS v4.1 Production Ready",
            "status": "healthy",
            "version": "4.1.0"
        }
    
    @fastapi_app.get("/health")
    async def health():
        return {"status": "healthy", "service": "AIRISS v4.1"}
    
    logger.info("✅ 헬스체크 엔드포인트 등록 완료")
    
except Exception as e:
    logger.error(f"❌ AIRISS 앱 로드 실패: {e}")
    import traceback
    traceback.print_exc()
    
    # 폴백 앱 생성
    from fastapi import FastAPI
    application = FastAPI()
    
    @application.get("/")
    async def fallback_root():
        return {"error": "AIRISS 로드 실패", "detail": str(e)}
    
    @application.get("/health")
    async def fallback_health():
        return {"status": "error", "error": str(e)}

# WSGI 호환성 (필요한 경우)
def create_app():
    return application

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
'''
    
    with open("application.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ application.py 수정 완료")

def create_fixed_procfile():
    """Procfile 수정 - 더 안정적인 설정"""
    
    content = "web: gunicorn application:application -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --keep-alive 2 --log-level info --access-logfile - --error-logfile -"
    
    with open("Procfile", "w") as f:
        f.write(content)
    
    print("✅ Procfile 수정 완료 (worker=1, timeout=120)")

def create_fixed_ebextensions():
    """EB Extensions 수정"""
    
    os.makedirs(".ebextensions", exist_ok=True)
    
    config_content = """option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
    ENVIRONMENT: "production"
    DEBUG: "false"
    PORT: "8000"
    HOST: "0.0.0.0"
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.medium
    IamInstanceProfile: aws-elasticbeanstalk-ec2-role
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 1
  aws:elasticbeanstalk:healthreporting:system:
    SystemType: enhanced
  aws:elasticbeanstalk:application:
    Application Healthcheck URL: /health
  aws:elasticbeanstalk:command:
    Timeout: 300
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py

commands:
  01_make_logs_dir:
    command: "mkdir -p /var/log/airiss"
  02_set_permissions:
    command: "chmod 755 /var/app/current"
"""
    
    with open(".ebextensions/01_python_fixed.config", "w") as f:
        f.write(config_content)
    
    print("✅ .ebextensions 수정 완료")

def create_simple_requirements():
    """최소한의 requirements.txt"""
    
    content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.7.0
pandas==2.1.3
numpy==1.24.3
openpyxl==3.1.2
python-multipart==0.0.6
aiofiles==23.2.1
sqlalchemy==2.0.23
aiosqlite==0.19.0
websockets==12.0
jinja2==3.1.2
python-dateutil==2.8.2
"""
    
    with open("requirements.txt", "w") as f:
        f.write(content)
    
    print("✅ requirements.txt 간소화 완료")

def create_emergency_fix_package():
    """긴급 수정 패키지 생성"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"airiss_v4_connection_fix_{timestamp}.zip"
    
    # 1. 파일들 수정
    create_fixed_application_py()
    create_fixed_procfile()
    create_fixed_ebextensions()
    create_simple_requirements()
    
    # 2. ZIP 패키지 생성
    files_to_include = [
        "app/",
        "static/",  # 존재하는 경우만
        ".ebextensions/",
        "application.py",
        "requirements.txt",
        "runtime.txt",
        "Procfile"
    ]
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in files_to_include:
            if os.path.exists(item):
                if os.path.isfile(item):
                    zipf.write(item)
                    print(f"✅ Added: {item}")
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        dirs[:] = [d for d in dirs if not d.startswith('__pycache__')]
                        for file in files:
                            if not file.endswith('.pyc'):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                    print(f"✅ Added directory: {item}")
    
    print(f"🎉 긴급 수정 패키지 생성: {package_name}")
    return package_name

def main():
    print("🚨 AIRISS v4.1 연결 타임아웃 긴급 수정")
    print("=" * 50)
    
    if not os.path.exists("app"):
        print("❌ app 디렉토리가 없습니다. AIRISS 프로젝트 루트에서 실행하세요.")
        return
    
    # 긴급 수정 패키지 생성
    package_name = create_emergency_fix_package()
    
    print("\n" + "=" * 50)
    print("🎯 즉시 실행 단계:")
    print("1. AWS Elastic Beanstalk 콘솔 접속")
    print("2. 환경 > 업로드 및 배포")
    print(f"3. {package_name} 파일 업로드")
    print("4. 배포 완료 후 5-10분 대기")
    print("\n💡 수정 사항:")
    print("- Worker 수 1개로 감소 (메모리 절약)")
    print("- 타임아웃 120초로 조정")
    print("- 로깅 강화")
    print("- 헬스체크 엔드포인트 강화")

if __name__ == "__main__":
    main()
