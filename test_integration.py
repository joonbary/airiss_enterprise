import asyncio
import aiohttp
import json
import websockets
from datetime import datetime
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AIRISSIntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.ws_url = "ws://localhost:8002/ws"
        self.test_results = []

    async def log_result(self, test_name, success, message):
        """테스트 결과 로깅"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} {test_name}: {message}"
        print(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": timestamp
        })

    async def test_backend_health(self):
        """백엔드 헬스체크 테스트"""
        try:
            async with aiohttp.ClientSession() as session:
                # 기본 헬스체크
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.log_result("Backend Health", True, f"Status: {data['status']}")
                        return True
                    else:
                        await self.log_result("Backend Health", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            await self.log_result("Backend Health", False, str(e))
            return False

    async def test_api_health(self):
        """API 헬스체크 테스트"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.log_result("API Health", True, f"React integration: {data.get('components', {}).get('react_integration', False)}")
                        return True
                    else:
                        await self.log_result("API Health", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            await self.log_result("API Health", False, str(e))
            return False

    async def test_websocket_connection(self):
        """WebSocket 연결 테스트"""
        try:
            client_id = f"test-client-{datetime.now().strftime('%H%M%S')}"
            uri = f"{self.ws_url}/{client_id}?channels=analysis,alerts"
            
            async with websockets.connect(uri) as websocket:
                # 연결 확인
                await self.log_result("WebSocket Connection", True, f"Connected as {client_id}")
                
                # 테스트 메시지 전송
                test_message = {
                    "type": "test",
                    "message": "Integration test message",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(test_message))
                
                # 응답 대기 (타임아웃 5초)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    await self.log_result("WebSocket Message", True, f"Received: {response_data.get('type', 'unknown')}")
                    return True
                except asyncio.TimeoutError:
                    await self.log_result("WebSocket Message", False, "No response within 5 seconds")
                    return False
                    
        except Exception as e:
            await self.log_result("WebSocket Connection", False, str(e))
            return False

    async def test_upload_endpoint(self):
        """파일 업로드 엔드포인트 테스트"""
        try:
            # 테스트용 가짜 파일 데이터 생성
            fake_file_data = b"test,data\n1,sample"
            
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file',
                             fake_file_data,
                             filename='test.csv',
                             content_type='text/csv')
                
                async with session.post(f"{self.base_url}/upload/upload/", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        await self.log_result("File Upload", True, f"File ID: {result.get('file_id', 'unknown')}")
                        return True
                    else:
                        await self.log_result("File Upload", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            await self.log_result("File Upload", False, str(e))
            return False

    async def test_analysis_jobs_endpoint(self):
        """분석 작업 목록 엔드포인트 테스트"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/analysis/jobs") as response:
                    if response.status == 200:
                        data = await response.json()
                        job_count = len(data) if isinstance(data, list) else 0
                        await self.log_result("Analysis Jobs", True, f"Found {job_count} jobs")
                        return True
                    else:
                        await self.log_result("Analysis Jobs", False, f"HTTP {response.status}")
                        return False
        except Exception as e:
            await self.log_result("Analysis Jobs", False, str(e))
            return False

    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("🧪 AIRISS v4.0 통합 테스트 시작")
        print("=" * 60)
        print()

        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("API Health Check", self.test_api_health),
            ("WebSocket Connection", self.test_websocket_connection),
            ("File Upload Endpoint", self.test_upload_endpoint),
            ("Analysis Jobs Endpoint", self.test_analysis_jobs_endpoint),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"🔍 {test_name} 테스트 실행 중...")
            success = await test_func()
            if success:
                passed += 1
            print()

        # 결과 요약
        print("=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"✅ 통과: {passed}/{total}")
        print(f"❌ 실패: {total - passed}/{total}")
        print(f"📈 성공률: {(passed/total)*100:.1f}%")
        print()

        if passed == total:
            print("🎉 모든 테스트가 성공했습니다!")
            print("🚀 AIRISS v4.0 시스템이 정상 작동 중입니다.")
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")
            print("🔧 서버가 실행 중인지 확인해주세요:")
            print("   - 백엔드: http://localhost:8002")
            print("   - React: http://localhost:3000 (개발 모드)")

        print()
        print("📋 상세 결과:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} [{result['timestamp']}] {result['test']}: {result['message']}")

        return passed == total

async def main():
    """메인 테스트 실행 함수"""
    tester = AIRISSIntegrationTest()
    success = await tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 통합 테스트 완료: 모든 시스템이 정상 작동합니다!")
    else:
        print("🔧 통합 테스트 완료: 일부 문제가 발견되었습니다.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        sys.exit(1)
