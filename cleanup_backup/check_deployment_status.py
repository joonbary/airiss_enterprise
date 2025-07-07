import requests
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
    
    print(f"\n📊 결과: {success_count}/{total_count} 엔드포인트 정상")
    
    if success_count == total_count:
        print("🎉 모든 엔드포인트가 정상 작동합니다!")
    elif success_count > 0:
        print("⚠️ 일부 엔드포인트만 작동합니다. 추가 확인 필요.")
    else:
        print("❌ 모든 엔드포인트 연결 실패. 배포 상태를 확인하세요.")

if __name__ == "__main__":
    check_deployment()
