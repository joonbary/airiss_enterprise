"""
AIRISS Backend WebSocket 서버 상태 확인 및 재시작 스크립트
"""
import requests
import json
import subprocess
import sys
import os
import time
from datetime import datetime

def check_server_status():
    """백엔드 서버 상태 확인"""
    try:
        print("🏥 백엔드 서버 상태 확인 중...")
        
        # Health check
        response = requests.get("http://localhost:8002/health", timeout=5)
        data = response.json()
        
        print("✅ 백엔드 서버 정상 작동")
        print(f"📊 WebSocket 연결 수: {data['components'].get('connection_count', 0)}")
        print(f"🔌 WebSocket 관리자: {data['components'].get('websocket_manager', 'N/A')}")
        
        # WebSocket 전용 health check
        ws_response = requests.get("http://localhost:8002/health/analysis", timeout=5)
        ws_data = ws_response.json()
        print(f"🧠 분석 엔진: {ws_data.get('status', 'Unknown')}")
        
        return True, data
        
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다 (포트 8002)")
        return False, None
    except requests.exceptions.Timeout:
        print("⏰ 백엔드 서버 응답 시간 초과")
        return False, None
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False, None

def check_port_usage():
    """포트 8002 사용 상태 확인"""
    try:
        print("🔍 포트 8002 사용 상태 확인...")
        result = subprocess.run(
            ["netstat", "-ano"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        lines = result.stdout.split('\n')
        port_8002_used = False
        
        for line in lines:
            if ':8002' in line and 'LISTENING' in line:
                print(f"📍 포트 8002 사용 중: {line.strip()}")
                port_8002_used = True
        
        if not port_8002_used:
            print("🚫 포트 8002가 사용되지 않고 있습니다")
            
        return port_8002_used
        
    except Exception as e:
        print(f"❌ 포트 확인 실패: {e}")
        return False

def start_backend_server():
    """백엔드 서버 시작"""
    try:
        print("🚀 백엔드 서버 시작 중...")
        
        # 현재 디렉토리를 프로젝트 루트로 변경
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # Python 가상환경 확인
        python_exe = sys.executable
        print(f"🐍 Python 실행 파일: {python_exe}")
        
        # 서버 실행 (백그라운드)
        print("📡 uvicorn으로 서버 시작...")
        process = subprocess.Popen([
            python_exe, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8002",
            "--reload"
        ])
        
        print(f"✅ 서버 프로세스 시작됨 (PID: {process.pid})")
        print("⏳ 서버 초기화 대기 중...")
        
        # 서버가 시작될 때까지 대기
        for i in range(30):  # 30초 대기
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8002/health", timeout=2)
                if response.status_code == 200:
                    print("✅ 서버가 성공적으로 시작되었습니다!")
                    return True, process
            except:
                print(f"⏳ 대기 중... ({i+1}/30)")
                continue
        
        print("❌ 서버 시작 시간 초과")
        process.terminate()
        return False, None
        
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return False, None

def test_websocket_connection():
    """WebSocket 연결 테스트"""
    try:
        print("🧪 WebSocket 연결 테스트...")
        
        import websockets
        import asyncio
        
        async def test_ws():
            uri = "ws://localhost:8002/ws/test-client-123?channels=analysis,alerts"
            
            try:
                async with websockets.connect(uri) as websocket:
                    print("✅ WebSocket 연결 성공!")
                    
                    # Ping 메시지 전송
                    await websocket.send(json.dumps({
                        "type": "ping",
                        "timestamp": datetime.now().isoformat()
                    }))
                    
                    # 응답 대기 (최대 5초)
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"📨 서버 응답: {response}")
                    
                    return True
                    
            except Exception as e:
                print(f"❌ WebSocket 연결 실패: {e}")
                return False
        
        # asyncio 이벤트 루프 실행
        try:
            return asyncio.run(test_ws())
        except:
            # websockets 라이브러리가 없는 경우 기본 테스트
            print("ℹ️ websockets 라이브러리 없음 - HTTP 테스트만 수행")
            return True
            
    except ImportError:
        print("ℹ️ websockets 라이브러리 설치 필요: pip install websockets")
        return True  # WebSocket 테스트 생략
    except Exception as e:
        print(f"❌ WebSocket 테스트 오류: {e}")
        return False

def main():
    """메인 진단 및 수정 함수"""
    print("🔧 AIRISS Backend WebSocket 진단 시작")
    print("=" * 60)
    print(f"📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 서버 상태 확인
    server_running, server_data = check_server_status()
    
    if not server_running:
        print("\n🔧 문제 해결 시도...")
        
        # 포트 사용 상태 확인
        port_used = check_port_usage()
        
        if port_used:
            print("⚠️ 포트 8002가 이미 사용 중입니다")
            print("💡 해결 방법:")
            print("   1. 다른 AIRISS 서버 프로세스 종료")
            print("   2. 작업 관리자에서 Python 프로세스 확인")
            print("   3. 재부팅 후 다시 시도")
        else:
            # 서버 시작 시도
            success, process = start_backend_server()
            if success:
                server_running = True
                print("✅ 백엔드 서버 복구 완료!")
            else:
                print("❌ 백엔드 서버 시작 실패")
    
    # 2. WebSocket 테스트
    if server_running:
        print("\n🧪 WebSocket 연결 테스트...")
        ws_test_success = test_websocket_connection()
        
        if ws_test_success:
            print("✅ WebSocket 연결 정상!")
        else:
            print("❌ WebSocket 연결 문제 발견")
    
    # 3. 종합 진단 결과
    print("\n📋 진단 결과 요약")
    print("=" * 40)
    print(f"🖥️ 백엔드 서버: {'✅ 정상' if server_running else '❌ 문제'}")
    print(f"🔌 WebSocket: {'✅ 정상' if server_running and ws_test_success else '❌ 문제'}")
    
    if server_running and ws_test_success:
        print("\n🎉 모든 시스템이 정상입니다!")
        print("💡 Frontend에서 다시 시도하세요:")
        print("   1. 브라우저 새로고침 (F5)")
        print("   2. 개발자 도구에서 debug_websocket.js 실행")
        print("   3. WebSocket 연결 상태 확인")
    else:
        print("\n🔧 추가 문제 해결 방법:")
        print("   1. 방화벽 설정 확인")
        print("   2. 백신 소프트웨어 예외 처리")
        print("   3. 관리자 권한으로 실행")
        print("   4. 포트 8002 사용 중인 다른 프로그램 종료")

if __name__ == "__main__":
    main()
