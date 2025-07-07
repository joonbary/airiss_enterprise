#!/usr/bin/env python3
"""
🔧 AWS AIRISS 배포 트러블슈팅 스크립트
연결 문제를 단계별로 진단하고 해결합니다.
"""

import requests
import subprocess
import json
import time
from datetime import datetime

class AWSDeploymentTroubleshooter:
    def __init__(self):
        self.url = "https://airiss-v4.ap-northeast-2.elasticbeanstalk.com"
        self.local_url = "http://localhost:8000"
        
    def check_1_basic_connectivity(self):
        """1단계: 기본 연결성 테스트"""
        print("🔍 1단계: 기본 연결성 테스트")
        print("=" * 50)
        
        endpoints = ["/", "/health", "/api", "/status"]
        
        for endpoint in endpoints:
            try:
                print(f"테스트 중: {self.url}{endpoint}")
                response = requests.get(f"{self.url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: 정상 (200)")
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"❌ {endpoint}: 연결 실패 (Connection Error)")
            except requests.exceptions.Timeout:
                print(f"❌ {endpoint}: 타임아웃 (Timeout)")
            except Exception as e:
                print(f"❌ {endpoint}: 오류 - {e}")
        
    def check_2_eb_status(self):
        """2단계: Elastic Beanstalk 상태 확인"""
        print("\n🔍 2단계: Elastic Beanstalk 상태 확인")
        print("=" * 50)
        
        try:
            # EB 상태 확인
            result = subprocess.run(['eb', 'status'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print("✅ EB CLI 연결 성공")
                print(result.stdout)
            else:
                print("❌ EB CLI 연결 실패")
                print("Error:", result.stderr)
                
        except FileNotFoundError:
            print("❌ EB CLI가 설치되지 않았습니다")
            print("해결책: pip install awsebcli")
        except Exception as e:
            print(f"❌ EB 상태 확인 실패: {e}")
    
    def check_3_eb_health(self):
        """3단계: EB 헬스 상태 확인"""
        print("\n🔍 3단계: EB 헬스 상태 확인")
        print("=" * 50)
        
        try:
            result = subprocess.run(['eb', 'health'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print("✅ EB 헬스 체크 성공")
                print(result.stdout)
            else:
                print("❌ EB 헬스 체크 실패")
                print("Error:", result.stderr)
                
        except Exception as e:
            print(f"❌ EB 헬스 확인 실패: {e}")
    
    def check_4_eb_logs(self):
        """4단계: EB 로그 확인"""
        print("\n🔍 4단계: EB 로그 확인 (최근 20줄)")
        print("=" * 50)
        
        try:
            result = subprocess.run(['eb', 'logs', '--all'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                
                print("📋 최근 로그:")
                for line in recent_lines:
                    if line.strip():
                        print(line)
            else:
                print("❌ EB 로그 가져오기 실패")
                print("Error:", result.stderr)
                
        except Exception as e:
            print(f"❌ EB 로그 확인 실패: {e}")
    
    def check_5_local_test(self):
        """5단계: 로컬 환경 테스트"""
        print("\n🔍 5단계: 로컬 환경 테스트")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.local_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ 로컬 서버 정상 작동")
                print("Local response:", response.json())
            else:
                print(f"❌ 로컬 서버 오류: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ 로컬 서버가 실행되지 않음")
            print("해결책: python application.py 실행")
        except Exception as e:
            print(f"❌ 로컬 테스트 실패: {e}")
    
    def get_solutions(self):
        """해결책 제시"""
        print("\n🛠️ 해결책 가이드")
        print("=" * 50)
        
        solutions = [
            {
                "문제": "Elastic Beanstalk 환경이 시작되지 않음",
                "해결책": [
                    "1. AWS Console에서 EB 환경 상태 확인",
                    "2. eb terminate 후 eb create 재실행",
                    "3. 인스턴스 타입을 t3.small로 변경"
                ]
            },
            {
                "문제": "보안 그룹 설정 문제",
                "해결책": [
                    "1. AWS Console → EC2 → Security Groups",
                    "2. EB 보안 그룹에 HTTP(80), HTTPS(443) 인바운드 추가",
                    "3. 소스: 0.0.0.0/0 (Anywhere)"
                ]
            },
            {
                "문제": "포트 설정 문제",
                "해결책": [
                    "1. application.py에서 port=8000 확인",
                    "2. .ebextensions에서 WSGIPath 확인",
                    "3. uvicorn 대신 gunicorn 사용 고려"
                ]
            },
            {
                "문제": "애플리케이션 코드 오류",
                "해결책": [
                    "1. eb logs로 상세 로그 확인",
                    "2. requirements.txt 의존성 확인",
                    "3. 최소 기능 버전으로 테스트"
                ]
            }
        ]
        
        for i, solution in enumerate(solutions, 1):
            print(f"\n{i}. {solution['문제']}")
            for step in solution['해결책']:
                print(f"   {step}")
    
    def quick_fix_commands(self):
        """빠른 수정 명령어"""
        print("\n⚡ 빠른 수정 명령어")
        print("=" * 50)
        
        commands = [
            "# 1. EB 환경 재시작",
            "eb deploy",
            "",
            "# 2. 새 환경 생성 (기존 문제가 있는 경우)",
            "eb create production-v2",
            "",
            "# 3. 로그 실시간 확인",
            "eb logs --all",
            "",
            "# 4. 환경 변수 설정 확인",
            "eb printenv",
            "",
            "# 5. 최소 버전으로 재배포",
            "# application.py만 사용하여 배포"
        ]
        
        for cmd in commands:
            print(cmd)
    
    def run_all_checks(self):
        """모든 체크 실행"""
        print("🚀 AIRISS AWS 배포 트러블슈팅 시작")
        print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.check_1_basic_connectivity()
        self.check_2_eb_status()
        self.check_3_eb_health()
        self.check_4_eb_logs()
        self.check_5_local_test()
        self.get_solutions()
        self.quick_fix_commands()
        
        print("\n✨ 트러블슈팅 완료!")
        print("문제가 지속되면 AWS Console에서 직접 확인하세요.")

if __name__ == "__main__":
    troubleshooter = AWSDeploymentTroubleshooter()
    troubleshooter.run_all_checks()
