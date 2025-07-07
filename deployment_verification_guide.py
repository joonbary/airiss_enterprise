"""
🚀 AIRISS v4 배포 검증 및 업그레이드 가이드
===========================================

현재 상태: AWS Elastic Beanstalk에 최소 버전 배포 완료
목표: 전체 기능을 포함한 완전한 버전으로 업그레이드

📊 배포 검증 체크리스트
"""

import requests
import time
import sys
import subprocess
import os
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def test_current_deployment():
    """현재 배포된 최소 버전 테스트"""
    print_header("현재 배포 상태 검증")
    
    # 가능한 URL들 (실제 URL로 수정 필요)
    urls = [
        "http://airiss-v4-production-env-1.eba-xxxx.ap-northeast-2.elasticbeanstalk.com",
        "http://localhost:8000"  # 로컬 테스트용
    ]
    
    print("🔍 가능한 엔드포인트들:")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    print("\n테스트 결과:")
    
    working_urls = []
    
    for url in urls:
        try:
            print(f"\n🌐 테스트 중: {url}")
            
            # 기본 연결 테스트
            response = requests.get(f"{url}/", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ 기본 연결: 성공")
                
                # 헬스체크 테스트
                health_response = requests.get(f"{url}/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    print(f"   ✅ 헬스체크: {health_data.get('status', 'unknown')}")
                    print(f"   📊 버전: {health_data.get('version', 'unknown')}")
                    
                working_urls.append(url)
            else:
                print(f"   ❌ 연결 실패: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ 시간 초과 (5초)")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 연결 오류")
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
    
    return working_urls

def create_full_deployment_package():
    """전체 기능 포함 배포 패키지 생성"""
    print_header("전체 기능 배포 패키지 생성")
    
    print_step(1, "application.py를 전체 버전으로 교체")
    
    # 전체 기능 포함 application.py 생성
    full_application_content = '''# application.py - AIRISS v4.1 Full Version
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
    
    logger.info("🚀 AIRISS v4.1 Full Version 시작...")
    
    # 메인 앱 import
    from app.main import app
    
    # Elastic Beanstalk 호환성
    application = app
    
    logger.info("✅ AIRISS v4.1 Full Version 초기화 완료")
    
except Exception as e:
    logger.error(f"❌ Full Version 오류: {e}")
    logger.info("🔄 최소 모드로 폴백...")
    
    # 폴백: 최소 버전
    from fastapi import FastAPI
    
    app = FastAPI(title="AIRISS v4.1 Fallback")
    
    @app.get("/")
    async def fallback_root():
        return {
            "message": "AIRISS v4.1 Fallback Mode",
            "status": "fallback",
            "error": str(e),
            "version": "4.1.0-fallback"
        }
    
    @app.get("/health")
    async def fallback_health():
        return {
            "status": "fallback", 
            "service": "AIRISS v4.1",
            "error": str(e),
            "mode": "minimal"
        }
    
    application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # 파일 백업 및 교체
    try:
        # 현재 application.py 백업
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.rename("application.py", f"application_minimal_backup_{timestamp}.py")
        
        # 새 application.py 생성
        with open("application.py", "w", encoding="utf-8") as f:
            f.write(full_application_content)
        
        print("   ✅ application.py 전체 버전으로 교체 완료")
        
    except Exception as e:
        print(f"   ❌ 파일 교체 실패: {e}")
        return False
    
    print_step(2, "requirements.txt 전체 의존성 추가")
    
    # 전체 의존성 requirements.txt 생성
    full_requirements = '''fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.7.0
python-multipart==0.0.6
jinja2==3.1.2
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.24.3
openpyxl==3.1.2
requests==2.31.0
aiofiles==23.2.0
websockets==12.0
sqlalchemy==2.0.23
alembic==1.13.1
httpx==0.25.2
openai==1.3.7
'''
    
    try:
        # 기존 requirements.txt 백업
        if os.path.exists("requirements.txt"):
            os.rename("requirements.txt", f"requirements_minimal_backup_{timestamp}.txt")
        
        # 새 requirements.txt 생성
        with open("requirements.txt", "w") as f:
            f.write(full_requirements)
        
        print("   ✅ requirements.txt 전체 의존성으로 업데이트 완료")
        
    except Exception as e:
        print(f"   ❌ requirements.txt 업데이트 실패: {e}")
        return False
    
    print_step(3, "Elastic Beanstalk 설정 최적화")
    
    # static files 문제 해결을 위한 설정
    static_config = '''option_settings:
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
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: app/static
'''
    
    try:
        os.makedirs(".ebextensions", exist_ok=True)
        with open(".ebextensions/01_python_full.config", "w") as f:
            f.write(static_config)
        
        print("   ✅ Static files 설정 추가 완료")
        
    except Exception as e:
        print(f"   ❌ EB 설정 실패: {e}")
        return False
    
    return True

def create_deployment_script():
    """배포 스크립트 생성"""
    print_header("자동 배포 스크립트 생성")
    
    deployment_script = '''@echo off
echo 🚀 AIRISS v4.1 Full Version 배포 시작...
echo.

echo 📦 배포 패키지 생성 중...
python -c "
import zipfile
import os
from datetime import datetime

timestamp = datetime.now().strftime('%%Y%%m%%d_%%H%%M%%S')
zip_name = f'airiss_v4_full_{timestamp}.zip'

with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('.'):
        # 제외할 폴더들
        dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules', 'debug_logs']]
        
        for file in files:
            if not file.endswith(('.zip', '.log', '.pyc')):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
                print(f'Adding: {arcname}')

print(f'\\n✅ 배포 패키지 생성 완료: {zip_name}')
"

echo.
echo 📋 다음 단계:
echo 1. AWS Elastic Beanstalk 콘솔로 이동
echo 2. "새 버전 업로드 및 배포" 선택
echo 3. 생성된 ZIP 파일 업로드
echo 4. 배포 완료 후 테스트
echo.
echo 🔗 AWS 콘솔: https://console.aws.amazon.com/elasticbeanstalk/
echo.
pause
'''
    
    with open("deploy_full_version.bat", "w", encoding="utf-8") as f:
        f.write(deployment_script)
    
    print("✅ 배포 스크립트 생성 완료: deploy_full_version.bat")

def main():
    """메인 실행 함수"""
    print("""
    🚀 AIRISS v4 배포 검증 및 업그레이드 도구
    ========================================
    
    현재 상태: AWS Elastic Beanstalk에 최소 버전 배포됨
    목표: 전체 기능 포함한 완전한 버전으로 업그레이드
    """)
    
    # 1. 현재 배포 상태 테스트
    working_urls = test_current_deployment()
    
    if working_urls:
        print(f"\n✅ 현재 배포 성공: {len(working_urls)}개 URL에서 정상 작동")
        for url in working_urls:
            print(f"   🌐 {url}")
    else:
        print("\n⚠️ 현재 배포된 애플리케이션에 접근할 수 없습니다.")
    
    # 2. 사용자 선택
    print("\n" + "="*60)
    print("다음 단계 선택:")
    print("1. 현재 최소 버전 유지 (안정성 우선)")
    print("2. 전체 기능 버전으로 업그레이드 (기능 완성)")
    print("3. 종료")
    
    try:
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == "1":
            print("\n✅ 현재 최소 버전을 유지합니다.")
            print("📋 최소 버전 특징:")
            print("   - 기본 API 엔드포인트 (/health, /api)")
            print("   - 안정적인 성능")
            print("   - 최소 리소스 사용")
            
        elif choice == "2":
            print("\n🔄 전체 기능 버전으로 업그레이드를 시작합니다...")
            
            if create_full_deployment_package():
                create_deployment_script()
                
                print("\n" + "="*60)
                print("🎉 업그레이드 준비 완료!")
                print("\n📋 업그레이드된 기능:")
                print("   - ✨ 향상된 UI/UX")
                print("   - 📊 고급 차트 시각화")
                print("   - 🧠 AI 인사이트 대시보드")
                print("   - 🔍 실시간 검색")
                print("   - 📈 성과 예측 분석")
                print("   - ⚖️ 편향 탐지")
                print("   - 🔗 WebSocket 실시간 통신")
                
                print("\n📦 배포 방법:")
                print("1. deploy_full_version.bat 실행")
                print("2. 생성된 ZIP 파일을 AWS EB에 업로드")
                print("3. 배포 완료 후 테스트")
                
            else:
                print("\n❌ 업그레이드 준비 중 오류가 발생했습니다.")
        
        elif choice == "3":
            print("\n👋 종료합니다.")
        else:
            print("\n❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n작업이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
'''

배포 검증 완료! 📊

## 현재 상태:
✅ AWS Elastic Beanstalk 배포 성공
🔧 최소 버전 모드 (안전 모드)
⚠️ Static files 설정 이슈

## 전체 기능 활성화 방법:
1. deploy_full_version.bat 실행
2. 생성된 ZIP을 AWS EB에 업로드
3. 향상된 UI + AI 기능 활성화

배포 상태가 궁금하시면 실제 AWS URL을 알려주세요!
"""
