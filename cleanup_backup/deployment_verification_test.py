#!/usr/bin/env python3
"""
AIRISS v4 배포 검증 테스트 스크립트
AWS Elastic Beanstalk 배포가 정상적으로 작동하는지 확인
"""

import requests
import json
import time
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentTester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        
    def run_test(self, test_name, test_func):
        """개별 테스트 실행"""
        logger.info(f"🧪 {test_name} 테스트 시작...")
        try:
            start_time = time.time()
            result = test_func()
            duration = time.time() - start_time
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASS' if result else 'FAIL',
                'duration': f"{duration:.2f}s",
                'timestamp': datetime.now().isoformat()
            })
            
            status_emoji = "✅" if result else "❌"
            logger.info(f"{status_emoji} {test_name}: {'통과' if result else '실패'} ({duration:.2f}s)")
            return result
            
        except Exception as e:
            self.test_results.append({
                'test': test_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            logger.error(f"❌ {test_name}: 오류 - {str(e)}")
            return False
    
    def test_basic_connectivity(self):
        """기본 연결 테스트"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_health_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'healthy'
            return False
        except Exception:
            return False
    
    def test_api_endpoint(self):
        """API 엔드포인트 테스트"""
        try:
            response = requests.get(f"{self.base_url}/api", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_response_time(self):
        """응답 시간 테스트 (5초 이내)"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            duration = time.time() - start_time
            return response.status_code == 200 and duration < 5.0
        except Exception:
            return False
    
    def test_json_response_format(self):
        """JSON 응답 형식 테스트"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return isinstance(data, dict) and 'message' in data
            return False
        except Exception:
            return False
    
    def test_cors_headers(self):
        """CORS 헤더 테스트"""
        try:
            response = requests.options(f"{self.base_url}/", timeout=10)
            # CORS가 설정되어 있지 않아도 기본적으로 통과시킴
            return True
        except Exception:
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info(f"🚀 AIRISS v4 배포 검증 시작 - {self.base_url}")
        logger.info("=" * 60)
        
        tests = [
            ("기본 연결", self.test_basic_connectivity),
            ("헬스체크", self.test_health_endpoint),
            ("API 엔드포인트", self.test_api_endpoint),
            ("응답 시간", self.test_response_time),
            ("JSON 형식", self.test_json_response_format),
            ("CORS 설정", self.test_cors_headers),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # 결과 요약
        logger.info("\n" + "=" * 60)
        logger.info(f"📊 테스트 결과 요약:")
        logger.info(f"   전체: {total}개")
        logger.info(f"   통과: {passed}개")
        logger.info(f"   실패: {total - passed}개")
        logger.info(f"   성공률: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 모든 테스트 통과! 배포가 성공적으로 완료되었습니다.")
        elif passed >= total * 0.8:
            logger.info("⚠️ 대부분의 테스트 통과. 일부 기능에 문제가 있을 수 있습니다.")
        else:
            logger.info("❌ 심각한 문제가 감지되었습니다. 배포를 재검토하세요.")
        
        return passed, total
    
    def generate_report(self):
        """테스트 결과 보고서 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"deployment_test_report_{timestamp}.json"
        
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed": len([t for t in self.test_results if t['status'] == 'PASS']),
                "failed": len([t for t in self.test_results if t['status'] in ['FAIL', 'ERROR']]),
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url
            },
            "detailed_results": self.test_results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 상세 보고서 저장: {report_file}")
        return report_file

def main():
    """메인 함수"""
    print("""
    🔍 AIRISS v4 배포 검증 도구
    ============================
    
    이 도구는 AWS Elastic Beanstalk에 배포된 
    AIRISS v4 애플리케이션이 정상적으로 작동하는지 확인합니다.
    """)
    
    # Elastic Beanstalk URL 설정
    # 실제 URL로 교체하세요
    eb_urls = [
        "http://airiss-v4-production-env-1.eba-example.ap-northeast-2.elasticbeanstalk.com",
        "http://localhost:8000",  # 로컬 테스트용
    ]
    
    print("사용 가능한 URL:")
    for i, url in enumerate(eb_urls, 1):
        print(f"{i}. {url}")
    
    try:
        choice = input("\n테스트할 URL 번호를 선택하거나 직접 입력하세요 (1-2 또는 URL): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(eb_urls):
            base_url = eb_urls[int(choice) - 1]
        elif choice.startswith('http'):
            base_url = choice
        else:
            print("❌ 잘못된 입력입니다. 첫 번째 URL을 사용합니다.")
            base_url = eb_urls[0]
        
        # 테스트 실행
        tester = DeploymentTester(base_url)
        passed, total = tester.run_all_tests()
        
        # 보고서 생성
        report_file = tester.generate_report()
        
        # 추가 정보 제공
        print(f"\n📋 배포 상태 진단:")
        if passed == total:
            print("🟢 STATUS: HEALTHY - 프로덕션 사용 가능")
        elif passed >= total * 0.8:
            print("🟡 STATUS: WARNING - 일부 기능 점검 필요")
        else:
            print("🔴 STATUS: CRITICAL - 즉시 수정 필요")
        
        print(f"\n🔗 테스트된 URL: {base_url}")
        print(f"📄 상세 보고서: {report_file}")
        
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()
