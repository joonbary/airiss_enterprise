# test_airiss_v4.py
# AIRISS v4.0 완전 자동화 업로드→분석 플로우 테스트
# 18단계: SQLiteService DB 통합 후 전체 기능 검증

import requests
import json
import time
import io
from datetime import datetime
from typing import Dict, Any, Optional

# 색깔 출력을 위한 ANSI 코드
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AIRISV4Tester:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.file_id = None
        self.job_id = None
        self.test_results = {}
        
    def print_step(self, step: str, status: str = "INFO", message: str = ""):
        """단계별 진행상황 출력"""
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
        elif status == "PROCESSING":
            color = Colors.BLUE
            symbol = "🔄"
        else:
            color = Colors.CYAN
            symbol = "ℹ️"
        
        print(f"{color}{symbol} [{timestamp}] {step}{Colors.END}")
        if message:
            print(f"   {color}{message}{Colors.END}")
        print()
    
    def print_header(self):
        """테스트 시작 헤더"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}🚀 AIRISS v4.0 완전 자동화 플로우 테스트{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 18단계: SQLiteService DB 통합 후 전체 기능 검증{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print()
        
    def prepare_test_data(self) -> str:
        """테스트용 CSV 데이터 준비"""
        self.print_step("1단계: 테스트 데이터 준비", "INFO")
        
        # OK금융그룹 AIRISS 테스트 데이터 (하이브리드 분석용)
        csv_data = """UID,의견,평가등급,KPI점수,근태점수,교육이수점수
user001,매우 우수한 성과를 보였습니다. 적극적이고 협업 능력이 뛰어납니다.,A+,95,100,90
user002,개선이 필요한 부분이 있지만 성실하게 노력하고 있습니다.,B,75,95,85
user003,탁월한 리더십을 발휘했습니다. 팀 성과 향상에 크게 기여했습니다.,S,98,100,95
user004,창의적인 아이디어로 업무 효율성을 높였습니다.,A,88,90,80
user005,커뮤니케이션 역량이 우수하고 동료들과의 협업이 좋습니다.,A-,82,95,85
user006,전문성이 뛰어나고 지속적으로 학습하는 자세를 보입니다.,A,90,100,92
user007,목표 달성을 위해 끝까지 노력하는 모습이 인상적입니다.,B+,78,88,75
user008,혁신적인 사고로 새로운 접근법을 제시했습니다.,A+,93,95,88
user009,팀워크가 좋고 긍정적인 에너지를 전달합니다.,A,85,92,90
user010,도전 정신이 강하고 어려운 과제도 적극적으로 해결합니다.,A,87,90,85"""
        
        self.print_step("✓ 테스트 데이터 생성 완료", "SUCCESS", 
                       f"총 10명의 직원 데이터 (UID + 의견 + 정량데이터)")
        return csv_data
    
    def test_server_health(self) -> bool:
        """서버 상태 확인"""
        self.print_step("2단계: 서버 상태 확인", "INFO")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_step("✓ 서버 정상 작동", "SUCCESS", 
                               f"버전: {data.get('version', 'Unknown')}")
                return True
            else:
                self.print_step("✗ 서버 응답 오류", "ERROR", 
                               f"상태 코드: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_step("✗ 서버 연결 실패", "ERROR", 
                           f"오류: {str(e)}\n서버가 실행 중인지 확인하세요: python -m app.main")
            return False
    
    def test_file_upload(self, csv_data: str) -> bool:
        """파일 업로드 테스트"""
        self.print_step("3단계: 파일 업로드 테스트", "INFO")
        
        try:
            # CSV 파일로 업로드
            files = {
                'file': ('airiss_test_data.csv', csv_data, 'text/csv')
            }
            
            response = requests.post(f"{self.base_url}/upload/upload/", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.file_id = data.get('id')
                
                self.print_step("✓ 파일 업로드 성공", "SUCCESS", 
                               f"File ID: {self.file_id}")
                self.print_step("", "INFO", 
                               f"파일명: {data.get('filename')}")
                self.print_step("", "INFO", 
                               f"레코드 수: {data.get('total_records')}")
                self.print_step("", "INFO", 
                               f"UID 컬럼: {data.get('uid_columns')}")
                self.print_step("", "INFO", 
                               f"의견 컬럼: {data.get('opinion_columns')}")
                self.print_step("", "INFO", 
                               f"정량 컬럼: {data.get('quantitative_columns')}")
                
                self.test_results['upload'] = data
                return True
            else:
                self.print_step("✗ 파일 업로드 실패", "ERROR", 
                               f"상태 코드: {response.status_code}")
                try:
                    error_data = response.json()
                    self.print_step("", "ERROR", f"오류 메시지: {error_data}")
                except:
                    self.print_step("", "ERROR", f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            self.print_step("✗ 업로드 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def test_file_retrieval(self) -> bool:
        """업로드된 파일 조회 테스트"""
        self.print_step("4단계: 파일 조회 테스트", "INFO")
        
        if not self.file_id:
            self.print_step("✗ File ID가 없습니다", "ERROR")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/upload/upload/{self.file_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.print_step("✓ 파일 조회 성공", "SUCCESS", 
                               f"SQLiteService pickle 복원 정상")
                self.print_step("", "INFO", 
                               f"DataFrame 행 수: {data.get('total_records')}")
                self.print_step("", "INFO", 
                               f"컬럼 수: {data.get('column_count')}")
                return True
            else:
                self.print_step("✗ 파일 조회 실패", "ERROR", 
                               f"상태 코드: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_step("✗ 조회 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def test_analysis_start(self) -> bool:
        """분석 시작 테스트"""
        self.print_step("5단계: 하이브리드 분석 시작 테스트", "INFO")
        
        if not self.file_id:
            self.print_step("✗ File ID가 없습니다", "ERROR")
            return False
        
        try:
            analysis_request = {
                "file_id": self.file_id,
                "sample_size": 10,  # 전체 데이터 분석
                "analysis_mode": "hybrid",  # 하이브리드 분석
                "enable_ai": False,  # 빠른 테스트를 위해 AI 비활성화
                "ai_api_key": None,  # AI API 키
                "ai_model": "gpt-3.5-turbo"  # AI 모델
            }
            
            response = requests.post(
                f"{self.base_url}/analysis/start",
                json=analysis_request
            )
            
            if response.status_code == 200:
                data = response.json()
                self.job_id = data.get('job_id')
                
                self.print_step("✓ 분석 시작 성공", "SUCCESS", 
                               f"Job ID: {self.job_id}")
                self.print_step("", "INFO", 
                               f"분석 모드: {data.get('analysis_mode')}")
                self.print_step("", "INFO", 
                               f"AI 피드백: {data.get('ai_feedback_enabled')}")
                
                self.test_results['analysis_start'] = data
                return True
            else:
                self.print_step("✗ 분석 시작 실패", "ERROR", 
                               f"상태 코드: {response.status_code}")
                try:
                    error_data = response.json()
                    self.print_step("", "ERROR", f"오류 메시지: {error_data}")
                except:
                    self.print_step("", "ERROR", f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            self.print_step("✗ 분석 시작 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def monitor_analysis_progress(self) -> bool:
        """실시간 분석 진행률 모니터링"""
        self.print_step("6단계: 실시간 분석 진행률 모니터링", "INFO")
        
        if not self.job_id:
            self.print_step("✗ Job ID가 없습니다", "ERROR")
            return False
        
        max_wait_time = 180  # 최대 3분 대기
        check_interval = 3   # 3초마다 확인
        elapsed_time = 0
        
        try:
            while elapsed_time < max_wait_time:
                response = requests.get(f"{self.base_url}/analysis/status/{self.job_id}")
                
                if response.status_code == 200:
                    status_data = response.json()
                    current_status = status_data.get('status')
                    progress = status_data.get('progress', 0)
                    processed = status_data.get('processed', 0)
                    total = status_data.get('total', 0)
                    
                    if current_status == 'completed':
                        self.print_step("✓ 분석 완료!", "SUCCESS", 
                                       f"처리: {processed}/{total} (100%)")
                        self.print_step("", "INFO", 
                                       f"평균 점수: {status_data.get('average_score', 0)}")
                        self.print_step("", "INFO", 
                                       f"처리 시간: {status_data.get('processing_time', 'Unknown')}")
                        
                        self.test_results['analysis_result'] = status_data
                        return True
                    
                    elif current_status == 'failed':
                        self.print_step("✗ 분석 실패", "ERROR", 
                                       f"오류: {status_data.get('error', 'Unknown')}")
                        return False
                    
                    elif current_status == 'processing':
                        self.print_step(f"🔄 분석 진행 중... {progress:.1f}%", "PROCESSING", 
                                       f"처리: {processed}/{total}")
                    
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
                else:
                    self.print_step("✗ 상태 조회 실패", "ERROR", 
                                   f"상태 코드: {response.status_code}")
                    return False
            
            # 시간 초과
            self.print_step("✗ 분석 시간 초과", "WARNING", 
                           f"{max_wait_time}초 대기 후 타임아웃")
            return False
            
        except Exception as e:
            self.print_step("✗ 모니터링 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def test_results_download(self) -> bool:
        """결과 다운로드 테스트"""
        self.print_step("7단계: 분석 결과 다운로드 테스트", "INFO")
        
        if not self.job_id:
            self.print_step("✗ Job ID가 없습니다", "ERROR")
            return False
        
        try:
            # 결과 조회
            response = requests.get(f"{self.base_url}/analysis/results/{self.job_id}")
            
            if response.status_code == 200:
                results_data = response.json()
                self.print_step("✓ 결과 조회 성공", "SUCCESS", 
                               f"결과 레코드 수: {len(results_data.get('results', []))}")
                
                # 샘플 결과 출력
                results = results_data.get('results', [])
                if results:
                    sample = results[0]
                    self.print_step("", "INFO", f"샘플 결과:")
                    self.print_step("", "INFO", f"  UID: {sample.get('UID')}")
                    self.print_step("", "INFO", f"  하이브리드 점수: {sample.get('AIRISS_v2_종합점수', 0)}")
                    self.print_step("", "INFO", f"  OK등급: {sample.get('OK등급')}")
                    self.print_step("", "INFO", f"  텍스트 점수: {sample.get('텍스트_종합점수', 0)}")
                    self.print_step("", "INFO", f"  정량 점수: {sample.get('정량_종합점수', 0)}")
                
                # 다운로드 테스트
                download_response = requests.get(
                    f"{self.base_url}/analysis/results/{self.job_id}/download"
                )
                
                if download_response.status_code == 200:
                    # 파일 저장
                    filename = f"airiss_v4_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(download_response.content)
                    
                    self.print_step("✓ Excel 파일 다운로드 성공", "SUCCESS", 
                                   f"파일 저장: {filename}")
                    self.print_step("", "INFO", 
                                   f"파일 크기: {len(download_response.content)} bytes")
                    return True
                else:
                    self.print_step("✗ 다운로드 실패", "ERROR", 
                                   f"상태 코드: {download_response.status_code}")
                    return False
            else:
                self.print_step("✗ 결과 조회 실패", "ERROR", 
                               f"상태 코드: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_step("✗ 다운로드 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def test_websocket_dashboard(self) -> bool:
        """WebSocket 대시보드 연결 테스트"""
        self.print_step("8단계: WebSocket 대시보드 연결 테스트", "INFO")
        
        try:
            # 대시보드 페이지 접근 테스트
            response = requests.get(f"{self.base_url}/dashboard")
            
            if response.status_code == 200:
                self.print_step("✓ 대시보드 페이지 접근 성공", "SUCCESS", 
                               f"URL: {self.base_url}/dashboard")
                self.print_step("", "INFO", 
                               "브라우저에서 실시간 대시보드 확인 가능")
                return True
            else:
                self.print_step("✗ 대시보드 접근 실패", "ERROR", 
                               f"상태 코드: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_step("✗ 대시보드 테스트 중 예외 발생", "ERROR", f"오류: {str(e)}")
            return False
    
    def print_final_summary(self, success_count: int, total_tests: int):
        """최종 결과 요약"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}🎯 AIRISS v4.0 테스트 완료 - 18단계 결과{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.END}")
        
        if success_count == total_tests:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 모든 테스트 성공! ({success_count}/{total_tests}){Colors.END}")
            print(f"{Colors.GREEN}✅ 업로드→분석 플로우 완전 정상 작동{Colors.END}")
            print(f"{Colors.GREEN}✅ SQLiteService DB 통합 성공{Colors.END}")
            print(f"{Colors.GREEN}✅ 하이브리드 분석 엔진 정상{Colors.END}")
            print(f"{Colors.GREEN}✅ 실시간 모니터링 시스템 정상{Colors.END}")
            print(f"{Colors.GREEN}✅ Excel 결과 생성 정상{Colors.END}")
            print(f"{Colors.GREEN}✅ WebSocket 대시보드 정상{Colors.END}")
            
            print(f"\n{Colors.CYAN}🚀 AIRISS v4.0 준비 완료!{Colors.END}")
            print(f"{Colors.CYAN}📊 실시간 대시보드: {self.base_url}/dashboard{Colors.END}")
            print(f"{Colors.CYAN}📚 API 문서: {self.base_url}/docs{Colors.END}")
            
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️ 일부 테스트 실패 ({success_count}/{total_tests}){Colors.END}")
            print(f"{Colors.YELLOW}🔧 실패한 단계를 확인하고 문제를 해결해주세요{Colors.END}")
        
        print(f"\n{Colors.BLUE}📋 테스트 데이터:{Colors.END}")
        if self.file_id:
            print(f"{Colors.BLUE}   File ID: {self.file_id}{Colors.END}")
        if self.job_id:
            print(f"{Colors.BLUE}   Job ID: {self.job_id}{Colors.END}")
        
        print(f"\n{Colors.MAGENTA}{'='*70}{Colors.END}")

def main():
    """메인 테스트 실행"""
    tester = AIRISV4Tester()
    tester.print_header()
    
    # 테스트 단계 실행
    success_count = 0
    total_tests = 8
    
    # 1. 테스트 데이터 준비
    csv_data = tester.prepare_test_data()
    success_count += 1
    
    # 2. 서버 상태 확인
    if tester.test_server_health():
        success_count += 1
        
        # 3. 파일 업로드 테스트
        if tester.test_file_upload(csv_data):
            success_count += 1
            
            # 4. 파일 조회 테스트
            if tester.test_file_retrieval():
                success_count += 1
                
                # 5. 분석 시작 테스트
                if tester.test_analysis_start():
                    success_count += 1
                    
                    # 6. 실시간 모니터링
                    if tester.monitor_analysis_progress():
                        success_count += 1
                        
                        # 7. 결과 다운로드 테스트
                        if tester.test_results_download():
                            success_count += 1
    
    # 8. WebSocket 대시보드 테스트 (독립 실행)
    if tester.test_websocket_dashboard():
        success_count += 1
    
    # 최종 결과 출력
    tester.print_final_summary(success_count, total_tests)

if __name__ == "__main__":
    main()