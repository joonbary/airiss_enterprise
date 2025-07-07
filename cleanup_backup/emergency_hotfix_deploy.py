#!/usr/bin/env python3
"""
AIRISS v4 긴급 수정 배포 스크립트 (Python 버전)
PowerShell 호환성 문제 해결
"""

import os
import shutil
import zipfile
from datetime import datetime
import subprocess
import sys

def print_step(step, description):
    print(f"\n{step} {description}")
    print("-" * 50)

def create_emergency_hotfix():
    """긴급 수정 배포 패키지 생성"""
    
    print("🚨 AIRISS v4 긴급 수정 배포")
    print("=" * 40)
    print("\n문제: /health 엔드포인트 연결 시간 초과")
    print("해결: 안정화된 application.py로 교체 후 재배포")
    
    # 1. 백업 생성
    print_step("1️⃣", "현재 application.py 백업 중...")
    
    if os.path.exists("application.py"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"application_backup_{timestamp}.py"
        shutil.copy2("application.py", backup_name)
        print(f"✅ 백업 완료: {backup_name}")
    else:
        print("❌ application.py 파일이 없습니다.")
        return False
    
    # 2. 안정화 버전으로 교체
    print_step("2️⃣", "안정화된 버전으로 교체 중...")
    
    if os.path.exists("application_stable.py"):
        shutil.copy2("application_stable.py", "application.py")
        print("✅ 안정화된 application.py로 교체 완료")
    else:
        print("❌ application_stable.py 파일이 없습니다.")
        return False
    
    # 3. 배포 패키지 생성
    print_step("3️⃣", "긴급 배포 패키지 생성 중...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"airiss_v4_hotfix_{timestamp}.zip"
    
    # 필수 파일들
    essential_files = [
        "application.py",
        "Procfile", 
        "requirements.txt"
    ]
    
    # runtime.txt가 있으면 포함
    if os.path.exists("runtime.txt"):
        essential_files.append("runtime.txt")
    
    # .ebextensions 파일들
    eb_files = []
    if os.path.exists(".ebextensions"):
        for root, dirs, files in os.walk(".ebextensions"):
            for file in files:
                eb_files.append(os.path.join(root, file))
    
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 필수 파일들 추가
            for file in essential_files:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"  Added: {file}")
                else:
                    print(f"  Warning: {file} not found")
            
            # EB 설정 파일들 추가
            for file in eb_files:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"  Added: {file}")
        
        print(f"\n✅ 긴급 배포 패키지 생성: {zip_name}")
        print(f"📦 파일 경로: {os.path.abspath(zip_name)}")
        
    except Exception as e:
        print(f"❌ ZIP 파일 생성 실패: {e}")
        return False
    
    # 4. 배포 후 테스트 스크립트 생성
    print_step("4️⃣", "배포 상태 확인 스크립트 생성...")
    
    test_script = '''import requests
import time

def check_deployment():
    url = "https://airiss-v4.ap-northeast-2.elasticbeanstalk.com"
    endpoints = ["/", "/health", "/api", "/status"]
    
    print("🔍 배포 후 상태 확인 중...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                success_count += 1
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Connection failed - {str(e)}")
    
    print(f"\\n📊 결과: {success_count}/{total_count} 엔드포인트 정상")
    
    if success_count == total_count:
        print("🎉 모든 엔드포인트가 정상 작동합니다!")
    elif success_count > 0:
        print("⚠️ 일부 엔드포인트만 작동합니다. 추가 확인 필요.")
    else:
        print("❌ 모든 엔드포인트 연결 실패. 배포 상태를 확인하세요.")

if __name__ == "__main__":
    check_deployment()
'''
    
    with open("check_deployment_status.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 상태 확인 스크립트 생성: check_deployment_status.py")
    
    return zip_name

def show_deployment_instructions(zip_name):
    """배포 안내 출력"""
    print("\n" + "=" * 60)
    print("🎉 긴급 수정 준비 완료!")
    print("=" * 60)
    
    print(f"\n📦 생성된 배포 파일: {zip_name}")
    print(f"📁 파일 위치: {os.path.abspath(zip_name)}")
    
    print("\n📋 다음 단계:")
    print("1. AWS Elastic Beanstalk 콘솔 접속")
    print("2. 환경: AIRISS-v4-Production-env-1 선택")
    print("3. '새 버전 업로드 및 배포' 클릭")
    print(f"4. {zip_name} 파일 업로드")
    print("5. 배포 완료 후 아래 명령으로 테스트:")
    print("   python check_deployment_status.py")
    
    print("\n🔗 AWS 콘솔: https://console.aws.amazon.com/elasticbeanstalk/")
    
    print("\n⏱️ 예상 배포 시간: 3-5분")
    print("📊 수정된 기능: 안정화된 모든 엔드포인트 (/health 포함)")
    
    print("\n🔧 수정 사항:")
    print("  ✅ 강화된 에러 핸들링")
    print("  ✅ 명시적 JSON 응답")
    print("  ✅ 추가 상태 확인 엔드포인트 (/status)")
    print("  ✅ 404/500 에러 핸들러")
    print("  ✅ 향상된 로깅")

def main():
    """메인 실행 함수"""
    print("Python 기반 긴급 수정 배포 도구")
    print("=" * 40)
    
    try:
        zip_name = create_emergency_hotfix()
        
        if zip_name:
            show_deployment_instructions(zip_name)
            
            # 사용자 선택
            print("\n" + "=" * 60)
            choice = input("배포 후 자동으로 상태 확인을 실행하시겠습니까? (y/n): ").strip().lower()
            
            if choice in ['y', 'yes', '예', 'ㅇ']:
                print("\n⏳ 배포 완료까지 대기 중...")
                print("(배포가 완료되면 Enter를 눌러 테스트를 시작하세요)")
                input()
                
                print("\n🔍 배포 상태 확인 중...")
                try:
                    subprocess.run([sys.executable, "check_deployment_status.py"])
                except Exception as e:
                    print(f"자동 테스트 실행 실패: {e}")
                    print("수동으로 'python check_deployment_status.py'를 실행하세요.")
        else:
            print("\n❌ 배포 패키지 생성에 실패했습니다.")
            
    except KeyboardInterrupt:
        print("\n\n작업이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()
