#!/usr/bin/env python3
"""
AIRISS v4.1 설정 파일 오류 긴급 수정
AWS Elastic Beanstalk 배포 실패 해결
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_clean_ebextensions():
    """깨끗한 .ebextensions 설정 생성"""
    
    os.makedirs(".ebextensions", exist_ok=True)
    
    # 수정된 설정 - staticfiles 옵션 제거
    config_content = """option_settings:
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: "/var/app/current"
    ENVIRONMENT: "production"
    DEBUG: "false"
    PORT: "8000"
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
"""
    
    with open(".ebextensions/01_python_clean.config", "w") as f:
        f.write(config_content)
    
    print("✅ 깨끗한 .ebextensions/01_python_clean.config 생성")

def create_minimal_application():
    """최소한의 application.py 생성"""
    
    content = '''# application.py - AWS Elastic Beanstalk 최소 버전
import os
import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 현재 디렉토리를 패스에 추가
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    logger.info("🚀 AIRISS 최소 버전 시작...")
    
    # FastAPI 임포트
    from fastapi import FastAPI
    
    # 최소한의 앱 생성
    app = FastAPI(title="AIRISS v4.1 Minimal")
    
    @app.get("/")
    async def root():
        return {
            "message": "AIRISS v4.1 Minimal Working!",
            "status": "healthy",
            "version": "4.1.0-minimal"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy", 
            "service": "AIRISS v4.1",
            "components": {
                "fastapi": "running",
                "basic_endpoints": "active"
            }
        }
    
    @app.get("/api")
    async def api_info():
        return {
            "message": "AIRISS v4.1 API",
            "status": "minimal_mode",
            "endpoints": ["/", "/health", "/api"]
        }
    
    # Elastic Beanstalk 호환성
    application = app
    
    logger.info("✅ AIRISS 최소 앱 초기화 완료")
    
except Exception as e:
    logger.error(f"❌ 오류 발생: {e}")
    
    # 완전 폴백 앱
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def emergency():
        return {"status": "emergency_mode", "error": str(e)}
    
    @app.get("/health") 
    async def emergency_health():
        return {"status": "error", "error": str(e)}
    
    application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("application.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ 최소한의 application.py 생성")

def create_minimal_requirements():
    """최소한의 dependencies만 포함"""
    
    content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.7.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(content)
    
    print("✅ 최소 requirements.txt 생성")

def create_fixed_procfile():
    """안정적인 Procfile"""
    
    content = "web: gunicorn application:application -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 60"
    
    with open("Procfile", "w") as f:
        f.write(content)
    
    print("✅ 안정적인 Procfile 생성")

def ensure_runtime():
    """runtime.txt 확인"""
    
    content = "python-3.11"
    
    with open("runtime.txt", "w") as f:
        f.write(content)
    
    print("✅ runtime.txt 확인")

def create_config_fix_package():
    """설정 수정 패키지 생성"""
    
    print("🔧 AIRISS v4.1 설정 오류 수정 패키지 생성 중...")
    
    # 1. 모든 설정 파일 수정
    create_clean_ebextensions()
    create_minimal_application()
    create_minimal_requirements()
    create_fixed_procfile()
    ensure_runtime()
    
    # 2. 기존 잘못된 설정 파일 제거
    old_config = ".ebextensions/01_python_fixed.config"
    if os.path.exists(old_config):
        os.remove(old_config)
        print(f"✅ 기존 문제 설정 파일 제거: {old_config}")
    
    # 3. ZIP 패키지 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"airiss_v4_config_fix_{timestamp}.zip"
    
    # 꼭 필요한 파일들만 포함
    essential_files = [
        ".ebextensions/01_python_clean.config",
        "application.py", 
        "requirements.txt",
        "runtime.txt",
        "Procfile"
    ]
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in essential_files:
            if os.path.exists(file_path):
                zipf.write(file_path)
                print(f"✅ 패키지에 포함: {file_path}")
            else:
                print(f"⚠️ 파일 없음: {file_path}")
    
    print(f"🎉 설정 수정 패키지 생성 완료: {package_name}")
    return package_name

def main():
    print("🚨 AIRISS v4.1 설정 파일 오류 긴급 수정")
    print("=" * 60)
    print("감지된 문제:")
    print("- ❌ Static files 설정 오류")
    print("- ❌ Configuration validation 실패")
    print("- ❌ Option specification 오류")
    print("=" * 60)
    
    # 긴급 수정 패키지 생성
    package_name = create_config_fix_package()
    
    print("\n" + "🎯 즉시 실행 단계:")
    print("1. AWS Elastic Beanstalk 콘솔 > 업로드 및 배포")
    print(f"2. {package_name} 업로드")
    print("3. 배포 완료 대기 (5-10분)")
    print("4. https://airiss-v4.ap-northeast-2.elasticbeanstalk.com/health 확인")
    
    print("\n" + "💡 수정 사항:")
    print("- ✅ 잘못된 staticfiles 설정 제거")
    print("- ✅ 최소한의 필수 설정만 유지")
    print("- ✅ 최소 FastAPI 앱으로 단순화")
    print("- ✅ Dependencies 최소화")
    
    print(f"\n📦 패키지 크기: {os.path.getsize(package_name) / 1024:.1f} KB")

if __name__ == "__main__":
    main()
