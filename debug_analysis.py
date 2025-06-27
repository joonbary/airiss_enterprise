# debug_analysis.py - 무한로딩 문제 디버깅용 스크립트

import requests
import json
from datetime import datetime

# 서버 URL
BASE_URL = "http://localhost:8002"

def test_analysis_flow():
    """분석 플로우 단계별 테스트"""
    print("🔍 AIRISS v4.0 분석 플로우 디버깅 시작")
    print("=" * 60)
    
    # 1. 헬스체크
    print("1️⃣ 헬스체크 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 서버 상태: {data.get('status')}")
            print(f"   📊 분석엔진: {data['components'].get('hybrid_analyzer')}")
            print(f"   🗄️ DB서비스: {data['components'].get('sqlite_service')}")
        else:
            print(f"   ❌ 헬스체크 실패: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 헬스체크 오류: {e}")
        return False
    
    # 2. 분석 엔진 헬스체크
    print("\n2️⃣ 분석 엔진 헬스체크...")
    try:
        response = requests.get(f"{BASE_URL}/health/analysis", timeout=5)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 분석엔진 상태: {data.get('status')}")
            print(f"   🧠 AI 프레임워크: {data.get('framework_dimensions')}개 영역")
        else:
            print(f"   ❌ 분석엔진 오류: {response.text}")
    except Exception as e:
        print(f"   ❌ 분석엔진 접속 오류: {e}")
    
    # 3. 파일 목록 확인
    print("\n3️⃣ 업로드된 파일 확인...")
    try:
        response = requests.get(f"{BASE_URL}/upload/files", timeout=10)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            files = response.json()
            print(f"   📁 업로드된 파일 수: {len(files)}")
            if files:
                latest_file = files[0]
                print(f"   📄 최신 파일: {latest_file.get('filename')}")
                print(f"   🆔 파일 ID: {latest_file.get('id')}")
                return latest_file.get('id')
            else:
                print("   ⚠️ 업로드된 파일이 없습니다")
                return None
    except Exception as e:
        print(f"   ❌ 파일 목록 조회 오류: {e}")
        return None

def test_analysis_start(file_id):
    """분석 시작 테스트"""
    print(f"\n4️⃣ 분석 시작 테스트 (파일 ID: {file_id})")
    
    analysis_data = {
        "file_id": file_id,
        "sample_size": 3,  # 작은 샘플로 테스트
        "analysis_mode": "hybrid",
        "enable_ai_feedback": False
    }
    
    try:
        print("   📤 분석 요청 전송 중...")
        response = requests.post(
            f"{BASE_URL}/analysis/start", 
            json=analysis_data,
            timeout=30
        )
        
        print(f"   상태코드: {response.status_code}")
        print(f"   응답 시간: {response.elapsed.total_seconds():.2f}초")
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"   ✅ 분석 시작 성공!")
            print(f"   🆔 Job ID: {job_id}")
            print(f"   📊 분석 모드: {data.get('analysis_mode')}")
            print(f"   ⏱️ 예상 시간: {data.get('estimated_time')}")
            return job_id
        else:
            print(f"   ❌ 분석 시작 실패: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ⏰ 분석 시작 요청 타임아웃 (30초)")
        return None
    except Exception as e:
        print(f"   ❌ 분석 시작 오류: {e}")
        return None

def monitor_analysis_progress(job_id, max_checks=20):
    """분석 진행률 모니터링"""
    print(f"\n5️⃣ 분석 진행률 모니터링 (Job ID: {job_id})")
    
    for i in range(max_checks):
        try:
            response = requests.get(f"{BASE_URL}/analysis/status/{job_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                processed = data.get('processed', 0)
                total = data.get('total', 0)
                
                print(f"   📊 [{i+1:2d}/20] 상태: {status} | 진행률: {progress:.1f}% ({processed}/{total})")
                
                if status == "completed":
                    print(f"   🎉 분석 완료! 평균 점수: {data.get('average_score', 0)}")
                    return True
                elif status == "failed":
                    print(f"   ❌ 분석 실패: {data.get('error', 'Unknown error')}")
                    return False
                    
            else:
                print(f"   ⚠️ 상태 조회 실패: {response.status_code}")
            
            # 2초 대기
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"   ❌ 상태 조회 오류: {e}")
    
    print("   ⏰ 모니터링 시간 초과 (40초)")
    return False

def main():
    """메인 테스트 함수"""
    print(f"🚀 AIRISS v4.0 무한로딩 디버깅")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 전체 플로우 테스트
    file_id = test_analysis_flow()
    
    if file_id:
        job_id = test_analysis_start(file_id)
        if job_id:
            success = monitor_analysis_progress(job_id)
            if success:
                print("\n🎉 전체 분석 플로우 성공!")
            else:
                print("\n❌ 분석 진행 중 문제 발생")
        else:
            print("\n❌ 분석 시작 실패")
    else:
        print("\n⚠️ 테스트할 파일이 없습니다. 먼저 파일을 업로드해주세요.")
    
    print(f"\n⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
