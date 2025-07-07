#!/usr/bin/env python3
"""
AIRISS v4.0 AWS 배포 검증 테스트
실제 배포된 환경에서 모든 엔드포인트 테스트
"""

import requests
import json
from datetime import datetime
import sys

# 배포된 URL
BASE_URL = "https://production.eba-i4ba22tu.ap-northeast-2.elasticbeanstalk.com"

def test_endpoint(endpoint, description):
    """개별 엔드포인트 테스트"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 테스트: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        print(f"✅ 상태코드: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📋 응답내용:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            except:
                print(f"📄 텍스트 응답: {response.text[:200]}...")
                return True
        else:
            print(f"❌ 오류: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 연결 오류: 서버에 연결할 수 없습니다")
        return False
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 서버 응답이 너무 느립니다")
        return False
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return False

def main():
    """메인 테스트 실행"""
    print("🎯 AIRISS v4.0 AWS 배포 검증 테스트")
    print("=" * 50)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 테스트할 엔드포인트들
    endpoints = [
        ("/", "루트 페이지"),
        ("/health", "헬스체크"),
        ("/api", "API 정보"),
        ("/status", "시스템 상태")
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        success = test_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    success_count = 0
    for endpoint, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{endpoint:15} → {status}")
        if success:
            success_count += 1
    
    total_tests = len(results)
    success_rate = (success_count / total_tests) * 100
    
    print(f"\n📈 성공률: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 모든 테스트 통과! 배포 성공!")
        return 0
    elif success_rate >= 75:
        print("⚠️ 대부분 성공, 일부 문제 있음")
        return 1
    else:
        print("❌ 심각한 문제 발견, 점검 필요")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
