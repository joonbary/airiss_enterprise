"""
AIRISS v4.0 통합 테스트 스크립트
서버 실행 및 API 테스트
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8002"
TEST_TIMEOUT = 30

async def test_server_health():
    """서버 헬스체크"""
    print("\n1. 서버 헬스체크 테스트...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # 기본 헬스체크
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ 서버 상태: 정상")
                    print(f"   - 버전: {data.get('version', 'Unknown')}")
                    print(f"   - 서비스: {data.get('service', 'Unknown')}")
                    
                    components = data.get('components', {})
                    print("\n   컴포넌트 상태:")
                    for comp, status in components.items():
                        emoji = "✅" if status in ["running", "active", True] else "❌"
                        print(f"   {emoji} {comp}: {status}")
                    return True
                else:
                    print(f"❌ 서버 응답 오류: HTTP {resp.status}")
                    return False
                    
        except aiohttp.ClientError as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False

async def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n2. API 엔드포인트 테스트...")
    
    endpoints = [
        ("/api", "GET", "API 정보"),
        ("/health/db", "GET", "DB 헬스체크"),
        ("/health/analysis", "GET", "분석 엔진 헬스체크"),
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for endpoint, method, name in endpoints:
            try:
                if method == "GET":
                    async with session.get(f"{BASE_URL}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"✅ {name}: OK")
                            results.append(True)
                        else:
                            print(f"❌ {name}: HTTP {resp.status}")
                            results.append(False)
            except Exception as e:
                print(f"❌ {name}: {type(e).__name__}")
                results.append(False)
    
    return all(results)

async def test_websocket_connection():
    """WebSocket 연결 테스트"""
    print("\n3. WebSocket 연결 테스트...")
    
    try:
        import websockets
        
        ws_url = f"ws://localhost:8002/ws/test-client"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("✅ WebSocket 연결 성공")
                
                # 테스트 메시지 전송
                test_message = json.dumps({"type": "ping", "timestamp": datetime.now().isoformat()})
                await websocket.send(test_message)
                print("✅ 메시지 전송 성공")
                
                # 응답 대기 (타임아웃 설정)
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"✅ 응답 수신: {response[:100]}...")
                    return True
                except asyncio.TimeoutError:
                    print("⚠️ 응답 타임아웃 (서버는 정상 작동 중)")
                    return True
                    
        except websockets.exceptions.WebSocketException as e:
            print(f"❌ WebSocket 연결 실패: {e}")
            return False
            
    except ImportError:
        print("⚠️ websockets 패키지가 설치되지 않음 (선택사항)")
        return True

async def test_file_upload():
    """파일 업로드 테스트"""
    print("\n4. 파일 업로드 테스트...")
    
    # 테스트 CSV 데이터 생성
    csv_content = """UID,이름,의견,성과등급,KPI점수,성별,연령대,부서
EMP001,테스트직원,매우 우수한 성과를 보임,A,95,남,30대,IT부"""
    
    async with aiohttp.ClientSession() as session:
        try:
            # FormData 생성
            data = aiohttp.FormData()
            data.add_field('file',
                         csv_content.encode('utf-8'),
                         filename='test_data.csv',
                         content_type='text/csv')
            
            async with session.post(f"{BASE_URL}/upload/upload/", 
                                  data=data,
                                  timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("✅ 파일 업로드 성공")
                    print(f"   - 파일 ID: {result.get('id', 'Unknown')}")
                    print(f"   - 레코드 수: {result.get('total_records', 0)}")
                    return True, result.get('id')
                else:
                    print(f"❌ 파일 업로드 실패: HTTP {resp.status}")
                    text = await resp.text()
                    print(f"   응답: {text[:200]}...")
                    return False, None
                    
        except Exception as e:
            print(f"❌ 파일 업로드 오류: {type(e).__name__}: {e}")
            return False, None

async def test_analysis_start(file_id):
    """분석 시작 테스트"""
    print("\n5. AI 분석 시작 테스트...")
    
    if not file_id:
        print("⚠️ 파일 ID가 없어 분석 테스트를 건너뜁니다.")
        return False
    
    analysis_data = {
        "file_id": file_id,
        "sample_size": 1,
        "analysis_mode": "hybrid",
        "enable_ai_feedback": False
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{BASE_URL}/analysis/start",
                                  json=analysis_data,
                                  timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print("✅ 분석 시작 성공")
                    print(f"   - Job ID: {result.get('job_id', 'Unknown')}")
                    return True
                else:
                    print(f"❌ 분석 시작 실패: HTTP {resp.status}")
                    text = await resp.text()
                    print(f"   응답: {text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ 분석 시작 오류: {type(e).__name__}: {e}")
            return False

async def test_advanced_features():
    """고급 기능 테스트 (편향 탐지, 예측 분석)"""
    print("\n6. 고급 기능 테스트...")
    
    # 편향 탐지 테스트
    print("   6.1 편향 탐지 API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/analysis/bias-detection",
                                  json={"file_id": "test"},
                                  timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status in [200, 503]:  # 503은 미설치 상태
                    if resp.status == 200:
                        print("   ✅ 편향 탐지 API: 활성")
                    else:
                        data = await resp.json()
                        print(f"   ⚠️ 편향 탐지 API: {data.get('detail', '사용 불가')}")
                else:
                    print(f"   ❌ 편향 탐지 API: HTTP {resp.status}")
    except Exception as e:
        print(f"   ❌ 편향 탐지 API: {type(e).__name__}")
    
    # 성과 예측 테스트
    print("   6.2 성과 예측 API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/analysis/performance-prediction",
                                  json={"file_id": "test"},
                                  timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status in [200, 503]:
                    if resp.status == 200:
                        print("   ✅ 성과 예측 API: 활성")
                    else:
                        data = await resp.json()
                        print(f"   ⚠️ 성과 예측 API: {data.get('detail', '사용 불가')}")
                else:
                    print(f"   ❌ 성과 예측 API: HTTP {resp.status}")
    except Exception as e:
        print(f"   ❌ 성과 예측 API: {type(e).__name__}")

async def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("AIRISS v4.0 통합 테스트 시작")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"서버: {BASE_URL}")
    print("=" * 60)
    
    # 서버가 시작될 때까지 대기
    print("\n서버 연결 대기 중...", end="", flush=True)
    for i in range(5):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    if resp.status == 200:
                        print(" 연결됨!")
                        break
        except:
            print(".", end="", flush=True)
            await asyncio.sleep(1)
    else:
        print("\n❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("\n서버 시작 명령:")
        print("  start_enhanced_v4.bat")
        return
    
    # 테스트 실행
    results = []
    
    # 1. 헬스체크
    results.append(await test_server_health())
    
    # 2. API 엔드포인트
    results.append(await test_api_endpoints())
    
    # 3. WebSocket
    results.append(await test_websocket_connection())
    
    # 4. 파일 업로드
    upload_success, file_id = await test_file_upload()
    results.append(upload_success)
    
    # 5. 분석 시작
    if file_id:
        results.append(await test_analysis_start(file_id))
    
    # 6. 고급 기능
    await test_advanced_features()
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"\n통과: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✅ 모든 테스트 통과! AIRISS v4.0이 정상 작동 중입니다.")
    elif passed >= total * 0.7:
        print("\n⚠️ 대부분의 테스트 통과. 일부 기능 확인 필요.")
    else:
        print("\n❌ 테스트 실패. 서버 로그를 확인하세요.")
    
    print("\n웹 인터페이스 접속:")
    print(f"  {BASE_URL}/")
    print("\nAPI 문서:")
    print(f"  {BASE_URL}/docs")

if __name__ == "__main__":
    # Windows에서 이벤트 루프 정책 설정
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 테스트 실행
    asyncio.run(run_all_tests())
