# simple_test_airiss_v4.py
# AIRISS v4.0 간단한 테스트 스크립트 (aiohttp 불필요)

import urllib.request
import json
import time
from datetime import datetime

def test_endpoint(url, name):
    """단일 엔드포인트 테스트"""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                print(f"✅ {name}: 정상")
                return True, result
            else:
                print(f"❌ {name}: HTTP {response.status}")
                return False, None
    except Exception as e:
        print(f"❌ {name}: 오류 - {str(e)}")
        return False, None

def main():
    base_url = "http://localhost:8002"
    
    print("🧪 AIRISS v4.0 간단한 연결 테스트")
    print("=" * 50)
    print(f"🎯 대상: {base_url}")
    print(f"🕐 시작: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # 테스트 엔드포인트들
    tests = [
        (f"{base_url}/", "기본 API"),
        (f"{base_url}/health", "헬스체크"),
        (f"{base_url}/health/db", "데이터베이스"),
        (f"{base_url}/health/analysis", "분석 엔진"),
        (f"{base_url}/upload/files/", "Upload 라우터"),
        (f"{base_url}/analysis/jobs", "Analysis 라우터"),
    ]
    
    success_count = 0
    total_count = len(tests)
    
    for url, name in tests:
        success, data = test_endpoint(url, name)
        if success:
            success_count += 1
        time.sleep(0.2)  # 잠시 대기
    
    print()
    print("=" * 50)
    print(f"📊 결과: {success_count}/{total_count} 테스트 통과")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과! AIRISS v4.0가 정상 작동합니다!")
        print()
        print("🚀 다음 단계:")
        print("   1. 대시보드 접속: http://localhost:8002/dashboard")
        print("   2. API 문서 확인: http://localhost:8002/docs")
        print("   3. 파일 업로드 테스트 진행")
        print("   4. 분석 작업 테스트 진행")
    elif success_count >= total_count * 0.8:
        print("⚠️ 대부분 정상이지만 일부 문제가 있습니다.")
        print("   - 위 오류를 확인하여 문제를 해결하세요.")
    else:
        print("❌ 여러 문제가 발생했습니다.")
        print("   - 서버가 정상 실행되었는지 확인하세요.")
        print("   - 포트 충돌이 해결되었는지 확인하세요.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()