#!/usr/bin/env python3
"""
🧪 AIRISS 로컬 환경 테스트
AWS 배포 전 로컬에서 정상 작동 확인
"""

import subprocess
import requests
import time
import os
import sys
from pathlib import Path

def test_local_application():
    """로컬 application.py 테스트"""
    print("🧪 로컬 환경 테스트 시작")
    print("=" * 50)
    
    # 1. application.py 존재 확인
    if not Path("application.py").exists():
        print("❌ application.py 파일이 없습니다!")
        return False
    
    print("✅ application.py 파일 확인")
    
    # 2. 로컬 서버 시작 (백그라운드)
    print("🚀 로컬 서버 시작 중...")
    try:
        # Python으로 서버 시작
        process = subprocess.Popen([
            sys.executable, "application.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 서버 시작 대기
        time.sleep(3)
        
        # 3. 엔드포인트 테스트
        base_url = "http://localhost:8000"
        endpoints = ["/", "/health", "/api", "/status"]
        
        success_count = 0
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                    success_count += 1
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        # 4. 프로세스 종료
        process.terminate()
        process.wait()
        
        print(f"\n📊 결과: {success_count}/{len(endpoints)} 엔드포인트 성공")
        
        if success_count == len(endpoints):
            print("🎉 로컬 환경 테스트 성공! AWS 배포 준비 완료")
            return True
        else:
            print("⚠️ 일부 엔드포인트 실패. 코드 수정 필요")
            return False
            
    except Exception as e:
        print(f"❌ 로컬 테스트 실패: {e}")
        return False

def check_requirements():
    """requirements.txt 의존성 확인"""
    print("\n📦 의존성 확인")
    print("=" * 30)
    
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt 파일이 없습니다!")
        return False
    
    try:
        # 주요 패키지 설치 확인
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
        
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 패키지 누락: {e}")
        print("해결책: pip install -r requirements.txt")
        return False

def test_eb_config():
    """EB 설정 파일 확인"""
    print("\n⚙️ EB 설정 확인")
    print("=" * 30)
    
    # .ebextensions 폴더 확인
    if Path(".ebextensions").exists():
        print("✅ .ebextensions 폴더 확인")
        
        config_files = list(Path(".ebextensions").glob("*.config"))
        print(f"✅ 설정 파일: {len(config_files)}개")
        
        for config_file in config_files:
            print(f"   - {config_file.name}")
    else:
        print("❌ .ebextensions 폴더 없음")
        return False
    
    # Procfile 확인
    if Path("Procfile").exists():
        print("✅ Procfile 확인")
    else:
        print("ℹ️ Procfile 없음 (선택사항)")
    
    return True

def main():
    """메인 테스트 실행"""
    print("🔧 AIRISS AWS 배포 전 테스트")
    print(f"현재 디렉토리: {os.getcwd()}")
    print("=" * 60)
    
    all_passed = True
    
    # 1. 의존성 확인
    if not check_requirements():
        all_passed = False
    
    # 2. EB 설정 확인
    if not test_eb_config():
        all_passed = False
    
    # 3. 로컬 애플리케이션 테스트
    if not test_local_application():
        all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 모든 테스트 통과! AWS 배포 가능")
        print("\n다음 단계:")
        print("1. eb deploy (재배포)")
        print("2. eb create production-v2 (새 환경)")
    else:
        print("❌ 일부 테스트 실패. 문제 해결 후 재시도")
        print("\n권장 해결책:")
        print("1. pip install -r requirements.txt")
        print("2. application.py 코드 확인")
        print("3. .ebextensions 설정 확인")

if __name__ == "__main__":
    main()
