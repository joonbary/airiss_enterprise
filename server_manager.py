#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 서버 시작 및 상태 확인
서버를 안전하게 시작하고 상태를 모니터링합니다.
"""

import os
import sys
import time
import subprocess
import threading
import httpx
import asyncio
from pathlib import Path

class AIRISSServerManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.server_process = None
        self.server_url = "http://localhost:8002"
        
    def check_port_availability(self, port=8002):
        """포트 사용 가능 여부 확인"""
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"⚠️  포트 {port}가 이미 사용 중입니다.")
            return False
        else:
            print(f"✅ 포트 {port} 사용 가능")
            return True
            
    def find_available_port(self, start_port=8002, max_port=8010):
        """사용 가능한 포트 찾기"""
        for port in range(start_port, max_port):
            if self.check_port_availability(port):
                return port
        return None
        
    async def wait_for_server(self, timeout=30):
        """서버 시작 대기"""
        print(f"\n⏳ 서버 시작 대기 중... (최대 {timeout}초)")
        
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    response = await client.get(f"{self.server_url}/health", timeout=2.0)
                    if response.status_code == 200:
                        print("✅ 서버가 성공적으로 시작되었습니다!")
                        return True
                except:
                    pass
                
                await asyncio.sleep(1)
                print(".", end="", flush=True)
                
        print("\n❌ 서버 시작 시간 초과")
        return False
        
    def start_server(self, port=8002):
        """서버 시작"""
        print(f"\n🚀 AIRISS v4.0 서버 시작 (포트: {port})")
        
        # 환경 변수 설정
        env = os.environ.copy()
        env['SERVER_PORT'] = str(port)
        env['WS_HOST'] = 'localhost'
        
        # Python 경로에 프로젝트 추가
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            
        # 서버 시작 명령
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ]
        
        try:
            # 서버 프로세스 시작
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 서버 출력 모니터링 스레드
            def monitor_output():
                for line in self.server_process.stdout:
                    print(f"  [서버] {line.strip()}")
                    
            monitor_thread = threading.Thread(target=monitor_output, daemon=True)
            monitor_thread.start()
            
            # 서버 시작 대기
            self.server_url = f"http://localhost:{port}"
            success = asyncio.run(self.wait_for_server())
            
            if success:
                self.show_server_info(port)
                return True
            else:
                self.stop_server()
                return False
                
        except Exception as e:
            print(f"❌ 서버 시작 실패: {e}")
            return False
            
    def show_server_info(self, port):
        """서버 정보 표시"""
        print("\n" + "="*60)
        print("✅ AIRISS v4.0 서버가 실행 중입니다!")
        print("="*60)
        print(f"\n📌 접속 정보:")
        print(f"  🏠 메인 페이지: http://localhost:{port}/")
        print(f"  📊 대시보드: http://localhost:{port}/dashboard")
        print(f"  📖 API 문서: http://localhost:{port}/docs")
        print(f"  🔍 헬스체크: http://localhost:{port}/health")
        print(f"\n💡 팁:")
        print(f"  - Ctrl+C를 눌러 서버를 종료할 수 있습니다")
        print(f"  - 파일 수정 시 자동으로 재시작됩니다 (--reload 모드)")
        print("\n" + "="*60)
        
    def stop_server(self):
        """서버 중지"""
        if self.server_process:
            print("\n🛑 서버 종료 중...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ 서버가 종료되었습니다.")
            
    def run_quick_test(self):
        """빠른 기능 테스트"""
        print("\n🧪 빠른 기능 테스트 실행...")
        
        async def test():
            async with httpx.AsyncClient() as client:
                # 헬스체크
                try:
                    response = await client.get(f"{self.server_url}/health")
                    data = response.json()
                    print(f"  ✅ 헬스체크: {data['status']}")
                    print(f"     - WebSocket 연결: {data['components']['websocket_manager']}")
                    print(f"     - SQLite: {data['components']['sqlite_service']}")
                    print(f"     - 분석 엔진: {data['components']['hybrid_analyzer']}")
                except Exception as e:
                    print(f"  ❌ 헬스체크 실패: {e}")
                    
                # API 정보
                try:
                    response = await client.get(f"{self.server_url}/api")
                    data = response.json()
                    print(f"\n  ✅ API 버전: {data['version']}")
                    features = data.get('features', {})
                    print(f"     - 하이브리드 분석: {features.get('hybrid_scoring', False)}")
                    print(f"     - 편향 탐지: {features.get('bias_detection', False)}")
                    print(f"     - 예측 분석: {features.get('performance_prediction', False)}")
                except Exception as e:
                    print(f"  ❌ API 정보 조회 실패: {e}")
                    
        asyncio.run(test())
        
    def interactive_mode(self):
        """대화형 모드"""
        print("\n🎮 AIRISS v4.0 서버 관리자")
        print("="*60)
        
        # 포트 확인
        port = 8002
        if not self.check_port_availability(port):
            available_port = self.find_available_port()
            if available_port:
                print(f"🔄 대체 포트 {available_port} 사용")
                port = available_port
            else:
                print("❌ 사용 가능한 포트가 없습니다.")
                return
                
        # 서버 시작
        if self.start_server(port):
            self.run_quick_test()
            
            try:
                print("\n💡 서버 실행 중... (종료하려면 Ctrl+C)")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⚠️  종료 신호 감지")
                self.stop_server()
        else:
            print("❌ 서버 시작에 실패했습니다.")
            
def main():
    manager = AIRISSServerManager()
    
    # 명령줄 인자 확인
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "test":
            # 테스트만 실행
            manager.server_url = "http://localhost:8002"
            manager.run_quick_test()
        else:
            print(f"알 수 없는 명령: {command}")
    else:
        # 기본: 대화형 모드
        manager.interactive_mode()

if __name__ == "__main__":
    main()
