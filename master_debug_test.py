#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 마스터 테스트 및 디버깅 도구
작성일: 2025.01.27
작성자: AI HR 전문가
"""

import os
import sys
import asyncio
import subprocess
import time
import json
import signal
from datetime import datetime
from pathlib import Path

class AIRISSDebugger:
    """AIRISS v4.0 디버깅 도구"""
    
    def __init__(self):
        self.server_process = None
        self.test_results = {}
        self.server_url = "http://localhost:8002"
        self.log_file = f"debug_logs/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 로그 디렉토리 생성
        os.makedirs("debug_logs", exist_ok=True)
    
    def log(self, message, level="INFO"):
        """로그 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # 콘솔 출력
        if level == "ERROR":
            print(f"\033[91m{log_message}\033[0m")
        elif level == "WARNING":
            print(f"\033[93m{log_message}\033[0m")
        elif level == "SUCCESS":
            print(f"\033[92m{log_message}\033[0m")
        else:
            print(log_message)
        
        # 파일 기록
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def check_requirements(self):
        """필수 요구사항 확인"""
        self.log("=== 필수 요구사항 확인 시작 ===")
        
        # Python 버전 확인
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.log(f"Python 버전: {python_version}")
        
        # 필수 패키지 확인
        required_packages = [
            'fastapi', 'uvicorn', 'pandas', 'numpy', 
            'sklearn', 'aiohttp', 'websockets', 'jinja2'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package if package != 'sklearn' else 'sklearn')
                self.log(f"✓ {package} 설치됨", "SUCCESS")
            except ImportError:
                self.log(f"✗ {package} 누락", "ERROR")
                missing_packages.append(package)
        
        if missing_packages:
            self.log(f"누락된 패키지: {', '.join(missing_packages)}", "ERROR")
            self.log("pip install -r requirements.txt 실행 필요", "WARNING")
            return False
        
        return True
    
    def check_file_structure(self):
        """파일 구조 확인"""
        self.log("=== 파일 구조 확인 시작 ===")
        
        critical_files = [
            "app/main.py",
            "app/services/hybrid_analyzer.py",
            "app/services/text_analyzer.py",
            "app/services/quantitative_analyzer.py",
            "app/db/sqlite_service.py",
            "app/templates/index.html"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if os.path.exists(file_path):
                self.log(f"✓ {file_path}", "SUCCESS")
            else:
                self.log(f"✗ {file_path} 누락", "ERROR")
                missing_files.append(file_path)
        
        return len(missing_files) == 0
    
    def start_server(self):
        """서버 시작"""
        self.log("=== 서버 시작 중 ===")
        
        try:
            # 기존 프로세스 종료
            self.stop_server()
            
            # 새 서버 시작
            cmd = [sys.executable, "-m", "uvicorn", "app.main:app", 
                   "--host", "0.0.0.0", "--port", "8002", "--reload"]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.log("서버 프로세스 시작됨", "SUCCESS")
            
            # 서버 시작 대기
            self.log("서버 초기화 대기 중...")
            time.sleep(5)
            
            # 서버 상태 확인
            import requests
            try:
                response = requests.get(f"{self.server_url}/health", timeout=5)
                if response.status_code == 200:
                    self.log("서버가 정상적으로 시작되었습니다", "SUCCESS")
                    return True
            except:
                pass
            
            self.log("서버 시작 실패", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"서버 시작 오류: {str(e)}", "ERROR")
            return False
    
    def stop_server(self):
        """서버 중지"""
        if self.server_process:
            self.log("기존 서버 프로세스 종료 중...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
            time.sleep(2)
    
    async def run_unit_tests(self):
        """단위 테스트 실행"""
        self.log("=== 단위 테스트 시작 ===")
        
        # 1. 텍스트 분석기 테스트
        try:
            from app.services.text_analyzer import AIRISSTextAnalyzer
            analyzer = AIRISSTextAnalyzer()
            result = analyzer.analyze_text("성과가 우수합니다", "업무성과")
            
            if result['score'] > 0:
                self.log("✓ 텍스트 분석기 테스트 통과", "SUCCESS")
                self.test_results['text_analyzer'] = True
            else:
                self.log("✗ 텍스트 분석기 결과 이상", "ERROR")
                self.test_results['text_analyzer'] = False
        except Exception as e:
            self.log(f"✗ 텍스트 분석기 오류: {str(e)}", "ERROR")
            self.test_results['text_analyzer'] = False
        
        # 2. 정량 분석기 테스트
        try:
            from app.services.quantitative_analyzer import QuantitativeAnalyzer
            analyzer = QuantitativeAnalyzer()
            scores = {'KPI달성률': 90, '출근율': 95}
            result = analyzer.analyze_scores(scores)
            
            if result['overall_score'] > 0:
                self.log("✓ 정량 분석기 테스트 통과", "SUCCESS")
                self.test_results['quant_analyzer'] = True
            else:
                self.log("✗ 정량 분석기 결과 이상", "ERROR")
                self.test_results['quant_analyzer'] = False
        except Exception as e:
            self.log(f"✗ 정량 분석기 오류: {str(e)}", "ERROR")
            self.test_results['quant_analyzer'] = False
        
        # 3. 하이브리드 분석기 테스트
        try:
            from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
            import pandas as pd
            
            analyzer = AIRISSHybridAnalyzer()
            test_data = pd.Series({
                'uid': 'TEST001',
                'opinion': '열심히 일하고 있습니다',
                'KPI달성률': 85,
                '출근율': 98
            })
            
            result = analyzer.comprehensive_analysis('TEST001', '열심히 일하고 있습니다', test_data)
            
            if 'hybrid_analysis' in result and result['hybrid_analysis']['overall_score'] > 0:
                self.log("✓ 하이브리드 분석기 테스트 통과", "SUCCESS")
                self.test_results['hybrid_analyzer'] = True
            else:
                self.log("✗ 하이브리드 분석기 결과 이상", "ERROR")
                self.test_results['hybrid_analyzer'] = False
        except Exception as e:
            self.log(f"✗ 하이브리드 분석기 오류: {str(e)}", "ERROR")
            self.test_results['hybrid_analyzer'] = False
    
    async def run_integration_tests(self):
        """통합 테스트 실행"""
        self.log("=== 통합 테스트 시작 ===")
        
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # API 연결 테스트
            try:
                async with session.get(f"{self.server_url}/api") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.log(f"✓ API 연결 성공 - 버전: {data.get('version')}", "SUCCESS")
                        self.test_results['api_connection'] = True
                    else:
                        self.log(f"✗ API 연결 실패 - 상태: {resp.status}", "ERROR")
                        self.test_results['api_connection'] = False
            except Exception as e:
                self.log(f"✗ API 연결 오류: {str(e)}", "ERROR")
                self.test_results['api_connection'] = False
            
            # 헬스체크 테스트
            try:
                async with session.get(f"{self.server_url}/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        components = data.get('components', {})
                        
                        self.log("✓ 헬스체크 성공", "SUCCESS")
                        self.log(f"  - FastAPI: {components.get('fastapi')}")
                        self.log(f"  - SQLite: {components.get('sqlite_service')}")
                        self.log(f"  - Analyzer: {components.get('hybrid_analyzer')}")
                        
                        self.test_results['health_check'] = True
                    else:
                        self.log(f"✗ 헬스체크 실패 - 상태: {resp.status}", "ERROR")
                        self.test_results['health_check'] = False
            except Exception as e:
                self.log(f"✗ 헬스체크 오류: {str(e)}", "ERROR")
                self.test_results['health_check'] = False
    
    def generate_report(self):
        """디버깅 보고서 생성"""
        self.log("=== 디버깅 보고서 ===")
        
        # 테스트 결과 요약
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        self.log(f"총 테스트: {total_tests}")
        self.log(f"성공: {passed_tests}")
        self.log(f"실패: {total_tests - passed_tests}")
        
        # 상세 결과
        self.log("\n상세 테스트 결과:")
        for test_name, result in self.test_results.items():
            status = "PASS" if result else "FAIL"
            if result:
                self.log(f"  {test_name}: {status}", "SUCCESS")
            else:
                self.log(f"  {test_name}: {status}", "ERROR")
        
        # 권장사항
        if passed_tests < total_tests:
            self.log("\n권장사항:", "WARNING")
            
            if not self.test_results.get('text_analyzer'):
                self.log("  - 텍스트 분석기 모듈 확인 필요")
            if not self.test_results.get('quant_analyzer'):
                self.log("  - 정량 분석기 모듈 확인 필요")
            if not self.test_results.get('hybrid_analyzer'):
                self.log("  - 하이브리드 분석기 통합 확인 필요")
            if not self.test_results.get('api_connection'):
                self.log("  - 서버 실행 상태 확인 필요")
        
        # 보고서 파일 생성
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests
            }
        }
        
        report_file = f"debug_logs/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"\n보고서 저장: {report_file}", "SUCCESS")
        self.log(f"로그 파일: {self.log_file}", "SUCCESS")
        
        return passed_tests == total_tests

async def main():
    """메인 실행 함수"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║        AIRISS v4.0 마스터 테스트 및 디버깅           ║
    ║      AI-based Resource Intelligence Scoring System     ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    debugger = AIRISSDebugger()
    
    try:
        # 1. 요구사항 확인
        if not debugger.check_requirements():
            debugger.log("필수 요구사항이 충족되지 않았습니다", "ERROR")
            return False
        
        # 2. 파일 구조 확인
        if not debugger.check_file_structure():
            debugger.log("필수 파일이 누락되었습니다", "ERROR")
            return False
        
        # 3. 단위 테스트
        await debugger.run_unit_tests()
        
        # 4. 서버 시작
        if debugger.start_server():
            # 5. 통합 테스트
            await debugger.run_integration_tests()
        
        # 6. 보고서 생성
        success = debugger.generate_report()
        
        if success:
            debugger.log("\n✅ 모든 테스트 통과! AIRISS v4.0이 정상 작동합니다.", "SUCCESS")
            debugger.log("\n다음 명령으로 서버를 실행하세요:", "SUCCESS")
            debugger.log("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload")
            debugger.log("\n또는 배치 파일 실행:")
            debugger.log("  start_airiss_correct.bat")
        else:
            debugger.log("\n⚠️ 일부 테스트 실패. 위의 권장사항을 확인하세요.", "WARNING")
        
        return success
        
    except KeyboardInterrupt:
        debugger.log("\n사용자에 의해 중단되었습니다", "WARNING")
        return False
    except Exception as e:
        debugger.log(f"\n예상치 못한 오류: {str(e)}", "ERROR")
        return False
    finally:
        # 서버 정리
        debugger.stop_server()

if __name__ == "__main__":
    # Windows 환경에서 색상 코드 활성화
    if sys.platform == "win32":
        os.system("color")
    
    # 비동기 함수 실행
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
