# quick_test.py
# AIRISS v4.0 빠른 연결성 테스트

import requests
import sys
import time
from datetime import datetime

def test_server_basic():
    """기본 서버 연결 테스트"""
    base_url = "http://localhost:8003"
    
    print("🚀 AIRISS v4.0 빠른 테스트 시작")
    print(f"📡 테스트 URL: {base_url}")
    print("-" * 50)
    
    # 1. 기본 연결 테스트
    try:
        print("1️⃣ 기본 연결 테스트...")
        response = requests.get(f"{base_url}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 서버 정상 응답 (버전: {data.get('version', 'Unknown')})")
            
            # 라우터 상태 확인
            if 'router_status' in data:
                print(f"   📋 라우터 상태: {data['router_status']}")
            
            return True
        else:
            print(f"   ❌ 서버 오류 (상태: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 서버 연결 실패 - 서버가 실행되지 않았습니다")
        print("\n🔧 서버 시작 방법:")
        print("   cd C:\\Users\\apro\\OneDrive\\Desktop\\AIRISS\\airiss_v4")
        print("   python -m app.main")
        print("   또는")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8003")
        return False
        
    except Exception as e:
        print(f"   ❌ 연결 테스트 오류: {str(e)}")
        return False

def test_routers():
    """라우터별 연결 테스트"""
    base_url = "http://localhost:8003"
    
    print("\n2️⃣ 라우터별 연결 테스트...")
    
    # Upload router 테스트
    try:
        response = requests.get(f"{base_url}/upload/files/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Upload router 정상")
        else:
            print(f"   ⚠️ Upload router 응답 오류 ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Upload router 오류: {str(e)}")
    
    # Analysis router 테스트 (이것이 핵심!)
    try:
        response = requests.get(f"{base_url}/analysis/jobs", timeout=5)
        if response.status_code == 200:
            print("   ✅ Analysis router 정상 - Import 오류 해결됨!")
        else:
            print(f"   ⚠️ Analysis router 응답 오류 ({response.status_code})")
    except Exception as e:
        print(f"   ❌ Analysis router 오류: {str(e)}")

def test_dashboard():
    """대시보드 접근 테스트"""
    base_url = "http://localhost:8003"
    
    print("\n3️⃣ 대시보드 접근 테스트...")
    
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("   ✅ 대시보드 페이지 정상")
            print(f"   🌐 브라우저에서 확인: {base_url}/dashboard")
        else:
            print(f"   ❌ 대시보드 오류 ({response.status_code})")
    except Exception as e:
        print(f"   ❌ 대시보드 테스트 오류: {str(e)}")

def main():
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_server_basic():
        test_routers()
        test_dashboard()
        
        print("\n" + "="*50)
        print("🎯 테스트 완료!")
        print("📊 전체 기능 테스트: python test_airiss_v4.py")
        print("📋 API 문서: http://localhost:8003/docs")
        print("🔌 실시간 대시보드: http://localhost:8003/dashboard")
        print("="*50)
    else:
        print("\n❌ 기본 연결 테스트 실패")
        sys.exit(1)

if __name__ == "__main__":
    main()
