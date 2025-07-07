#!/usr/bin/env python3
"""
빠른 API 테스트 스크립트
실제 API 엔드포인트가 작동하는지 확인
"""

import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8002"
    
    print("🧪 AIRISS API 테스트")
    print("=" * 50)
    
    # 1. 헬스 체크
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Server: {response.json().get('service', 'N/A')}")
    except Exception as e:
        print(f"❌ Health Check 실패: {e}")
        return
    
    # 2. 완료된 작업 목록 조회
    try:
        response = requests.get(f"{base_url}/analysis/jobs")
        print(f"✅ Jobs List: {response.status_code}")
        if response.status_code == 200:
            jobs = response.json()
            completed_jobs = [job for job in jobs if job.get('status') == 'completed']
            print(f"   완료된 작업: {len(completed_jobs)}개")
            
            if completed_jobs:
                test_job = completed_jobs[0]
                job_id = test_job['id']
                print(f"   테스트 Job ID: {job_id[:8]}...")
                
                # 3. 직원 검색 테스트
                search_url = f"{base_url}/api/v1/employee/{job_id}"
                response = requests.get(search_url)
                print(f"✅ Employee Search: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    employee = result.get('employee', {})
                    print(f"   검색된 직원: {employee.get('UID', 'N/A')}")
                    print(f"   점수: {employee.get('AIRISS_v2_종합점수', 'N/A')}")
                    print(f"   등급: {employee.get('OK등급', 'N/A')}")
                else:
                    print(f"   ❌ 오류: {response.text}")
            else:
                print("   ⚠️ 완료된 작업이 없습니다")
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")

if __name__ == "__main__":
    test_api_endpoints()
