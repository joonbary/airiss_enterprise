# diagnose_job_id.py
# AIRISS v4.0 Job ID 불일치 문제 전용 진단 스크립트

import requests
import json
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class JobIDDiagnoser:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.file_id = None
        self.requested_job_id = None
        self.returned_job_id = None
        
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
    
    def check_server_status(self):
        """서버 상태 확인"""
        self.print_step("🔍 서버 상태 확인 중...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_step("서버 정상 작동", "SUCCESS")
                return True
            else:
                self.print_step(f"서버 응답 오류: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_step(f"서버 연결 실패: {e}", "ERROR")
            self.print_step("해결방법: python -m app.main 명령으로 서버를 실행하세요", "WARNING")
            return False
    
    def upload_test_file(self):
        """테스트 파일 업로드"""
        self.print_step("📁 테스트 파일 업로드 중...")
        
        # 간단한 테스트 데이터
        csv_data = """UID,의견,평가등급
user001,매우 우수한 성과를 보였습니다,A+
user002,개선이 필요한 부분이 있습니다,B"""
        
        try:
            files = {'file': ('test_job_id.csv', csv_data, 'text/csv')}
            response = requests.post(f"{self.base_url}/upload/upload/", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.file_id = data.get('id')
                self.print_step(f"파일 업로드 성공: {self.file_id}", "SUCCESS")
                return True
            else:
                self.print_step(f"업로드 실패: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.print_step(f"업로드 오류: {e}", "ERROR")
            return False
    
    def test_job_id_consistency(self):
        """핵심: Job ID 일치성 테스트"""
        self.print_step("🎯 Job ID 일치성 테스트 시작...")
        
        if not self.file_id:
            self.print_step("File ID가 없습니다", "ERROR")
            return False
        
        try:
            # 분석 요청
            analysis_request = {
                "file_id": self.file_id,
                "sample_size": 2,
                "analysis_mode": "hybrid"
            }
            
            self.print_step("📤 분석 요청 전송 중...")
            response = requests.post(f"{self.base_url}/analysis/start", json=analysis_request)
            
            if response.status_code == 200:
                data = response.json()
                self.returned_job_id = data.get('job_id')
                
                self.print_step(f"분석 시작 응답 수신", "SUCCESS")
                self.print_step(f"반환된 Job ID: {self.returned_job_id}")
                
                # 즉시 상태 조회로 ID 일치성 확인
                return self.verify_job_id_immediately()
                
            else:
                self.print_step(f"분석 시작 실패: {response.status_code}", "ERROR")
                try:
                    error_detail = response.json()
                    self.print_step(f"오류 상세: {error_detail}", "ERROR")
                except:
                    self.print_step(f"응답 내용: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.print_step(f"테스트 중 예외 발생: {e}", "ERROR")
            return False
    
    def verify_job_id_immediately(self):
        """즉시 Job ID 검증"""
        self.print_step("🔍 Job ID 검증 중...")
        
        if not self.returned_job_id:
            self.print_step("반환된 Job ID가 없습니다", "ERROR")
            return False
        
        try:
            # 바로 상태 조회 시도
            response = requests.get(f"{self.base_url}/analysis/status/{self.returned_job_id}")
            
            if response.status_code == 200:
                status_data = response.json()
                db_job_id = status_data.get('job_id')
                
                self.print_step("상태 조회 성공", "SUCCESS")
                self.print_step(f"요청 Job ID: {self.returned_job_id}")
                self.print_step(f"DB Job ID: {db_job_id}")
                
                if db_job_id == self.returned_job_id:
                    self.print_step("🎉 Job ID 완전 일치! 문제 해결됨", "SUCCESS")
                    return True
                else:
                    self.print_step("❌ Job ID 불일치 문제 여전히 존재", "ERROR")
                    return False
                    
            elif response.status_code == 404:
                self.print_step("404 오류: Job을 찾을 수 없음 - Job ID 불일치 문제", "ERROR")
                return False
            else:
                self.print_step(f"상태 조회 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_step(f"검증 중 오류: {e}", "ERROR")
            return False
    
    def wait_and_check_final_status(self):
        """잠시 대기 후 최종 상태 확인"""
        self.print_step("⏰ 3초 대기 후 최종 상태 확인...")
        time.sleep(3)
        
        try:
            response = requests.get(f"{self.base_url}/analysis/status/{self.returned_job_id}")
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                
                self.print_step(f"최종 상태: {status} (진행률: {progress}%)", "SUCCESS")
                
                if status in ['processing', 'completed']:
                    self.print_step("분석이 정상적으로 진행되고 있습니다", "SUCCESS")
                    return True
                else:
                    self.print_step(f"비정상 상태: {status}", "WARNING")
                    return False
            else:
                self.print_step(f"최종 상태 확인 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.print_step(f"최종 확인 중 오류: {e}", "ERROR")
            return False
    
    def run_diagnosis(self):
        """전체 진단 실행"""
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 AIRISS v4.0 Job ID 불일치 문제 진단{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print()
        
        success_count = 0
        total_tests = 4
        
        # 1. 서버 상태 확인
        if self.check_server_status():
            success_count += 1
            
            # 2. 파일 업로드
            if self.upload_test_file():
                success_count += 1
                
                # 3. Job ID 일치성 테스트 (핵심)
                if self.test_job_id_consistency():
                    success_count += 1
                    
                    # 4. 최종 상태 확인
                    if self.wait_and_check_final_status():
                        success_count += 1
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        
        if success_count == total_tests:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 모든 테스트 성공! Job ID 문제 완전 해결됨{Colors.END}")
            print(f"{Colors.GREEN}✅ Job ID 일치성 확인 완료{Colors.END}")
            print(f"{Colors.GREEN}✅ 404 오류 해결됨{Colors.END}")
            print(f"{Colors.GREEN}✅ SQLiteService 정상 작동{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️ 테스트 실패 ({success_count}/{total_tests}){Colors.END}")
            if success_count < 3:
                print(f"{Colors.YELLOW}🔧 Job ID 불일치 문제가 여전히 존재합니다{Colors.END}")
                print(f"{Colors.YELLOW}📋 코드 수정이 필요할 수 있습니다{Colors.END}")
        
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")

def main():
    diagnoser = JobIDDiagnoser()
    diagnoser.run_diagnosis()

if __name__ == "__main__":
    main()
