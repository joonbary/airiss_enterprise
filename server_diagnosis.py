# server_diagnosis.py
# AIRISS v4.0 서버 오류 진단 스크립트

import requests
import subprocess
import sys
import traceback
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ServerDiagnoser:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        
    def print_step(self, message: str, status: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if status == "SUCCESS":
            color = Colors.GREEN
            symbol = "✅"
        elif status == "ERROR":
            color = Colors.RED
            symbol = "❌"
        elif status == "WARNING":
            color = Colors.YELLOW
            symbol = "⚠️"
        else:
            color = Colors.BLUE
            symbol = "ℹ️"
        
        print(f"{color}{symbol} [{timestamp}] {message}{Colors.END}")
    
    def check_server_process(self):
        """서버 프로세스 확인"""
        self.print_step("🔍 서버 프로세스 확인 중...")
        
        try:
            # Windows에서 포트 8002를 사용하는 프로세스 확인
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
            
            if ':8002' in result.stdout:
                self.print_step("포트 8002에서 서버 실행 중", "SUCCESS")
                return True
            else:
                self.print_step("포트 8002에서 실행 중인 서버 없음", "ERROR")
                return False
                
        except Exception as e:
            self.print_step(f"프로세스 확인 오류: {e}", "ERROR")
            return False
    
    def test_server_endpoints(self):
        """각 엔드포인트별 상태 확인"""
        endpoints = [
            "/",
            "/health", 
            "/health/db",
            "/health/analysis"
        ]
        
        for endpoint in endpoints:
            try:
                self.print_step(f"테스트: {endpoint}")
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 200:
                    self.print_step(f"{endpoint} - 정상 (200)", "SUCCESS")
                else:
                    self.print_step(f"{endpoint} - 오류 ({response.status_code})", "ERROR")
                    try:
                        error_detail = response.json()
                        print(f"   상세: {error_detail}")
                    except:
                        print(f"   응답: {response.text[:200]}...")
                        
            except requests.exceptions.ConnectionError:
                self.print_step(f"{endpoint} - 연결 실패", "ERROR")
            except requests.exceptions.Timeout:
                self.print_step(f"{endpoint} - 타임아웃", "ERROR")
            except Exception as e:
                self.print_step(f"{endpoint} - 예외: {e}", "ERROR")
    
    def check_import_issues(self):
        """Import 문제 확인"""
        self.print_step("🔍 Import 문제 확인 중...")
        
        try:
            # 핵심 모듈들 import 테스트
            sys.path.append('.')
            
            # 1. 메인 앱 import
            from app.main import app
            self.print_step("app.main import 성공", "SUCCESS")
            
            # 2. SQLiteService import  
            from app.db.sqlite_service import SQLiteService
            self.print_step("SQLiteService import 성공", "SUCCESS")
            
            # 3. Analysis API import
            from app.api.analysis import router
            self.print_step("Analysis API import 성공", "SUCCESS")
            
            # 4. WebSocket Manager import
            from app.core.websocket_manager import ConnectionManager
            self.print_step("WebSocket Manager import 성공", "SUCCESS")
            
            return True
            
        except ImportError as ie:
            self.print_step(f"Import 오류 발견: {ie}", "ERROR")
            print(f"   {traceback.format_exc()}")
            return False
        except Exception as e:
            self.print_step(f"Import 테스트 중 예외: {e}", "ERROR")
            print(f"   {traceback.format_exc()}")
            return False
    
    def check_database_connection(self):
        """데이터베이스 연결 확인"""
        self.print_step("🔍 데이터베이스 연결 확인 중...")
        
        try:
            from app.db.sqlite_service import SQLiteService
            import asyncio
            
            async def test_db():
                db_service = SQLiteService()
                await db_service.init_database()
                stats = await db_service.get_database_stats()
                return stats
            
            # asyncio 이벤트 루프 실행
            stats = asyncio.run(test_db())
            
            self.print_step("데이터베이스 연결 성공", "SUCCESS")
            self.print_step(f"통계: {stats}", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_step(f"데이터베이스 연결 오류: {e}", "ERROR")
            print(f"   {traceback.format_exc()}")
            return False
    
    def run_diagnosis(self):
        """전체 진단 실행"""
        print(f"{Colors.BOLD}{Colors.RED}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}🚨 AIRISS v4.0 서버 500 오류 진단{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'='*70}{Colors.END}")
        print()
        
        # 1. 서버 프로세스 확인
        process_running = self.check_server_process()
        
        # 2. 엔드포인트별 테스트
        if process_running:
            self.test_server_endpoints()
        
        # 3. Import 문제 확인
        import_ok = self.check_import_issues()
        
        # 4. 데이터베이스 연결 확인
        if import_ok:
            db_ok = self.check_database_connection()
        
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}🔧 권장 해결 방법:{Colors.END}")
        
        if not process_running:
            print(f"{Colors.YELLOW}1. 서버를 실행하세요: python -m app.main{Colors.END}")
        elif not import_ok:
            print(f"{Colors.YELLOW}1. Import 오류를 수정하세요{Colors.END}")
            print(f"{Colors.YELLOW}2. 가상환경이 활성화되어 있는지 확인하세요{Colors.END}")
        else:
            print(f"{Colors.YELLOW}1. 서버를 재시작해보세요{Colors.END}")
            print(f"{Colors.YELLOW}2. 로그 파일을 확인하세요: airiss_v4.log{Colors.END}")
            print(f"{Colors.YELLOW}3. 포트 충돌을 확인하세요{Colors.END}")
        
        print(f"{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")

def main():
    diagnoser = ServerDiagnoser()
    diagnoser.run_diagnosis()

if __name__ == "__main__":
    main()
