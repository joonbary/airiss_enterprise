# full_test.py
import requests
import asyncio
import websockets
import json
import threading
import time

BASE_URL = "http://localhost:8001/api/v1"

def upload_test_file():
    """테스트 파일 업로드"""
    print("📁 테스트 파일 업로드 중...")
    
    # 테스트 CSV 파일 생성
    import pandas as pd
    
    test_data = {
        'UID': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005'],
        '평가의견': [
            '업무 성과가 매우 우수하고 팀워크도 뛰어남. KPI 목표를 초과 달성했으며 창의적인 아이디어로 프로세스를 개선함.',
            '성실하고 책임감이 강함. 커뮤니케이션 능력이 다소 부족하지만 전문성은 높은 수준임.',
            '리더십이 뛰어나고 팀원들과의 협업이 원활함. 다만 시간 관리 능력은 개선이 필요함.',
            '창의적이고 혁신적인 사고를 가지고 있음. 조직 적응력이 높고 새로운 도전을 두려워하지 않음.',
            '기본적인 업무는 잘 수행하나 적극성이 부족함. 학습 의지는 있으나 실행력이 떨어짐.'
        ],
        '성과등급': ['S', 'A', 'A', 'B', 'C'],
        'KPI달성률': [120, 95, 100, 85, 70],
        '역량점수': [95, 85, 88, 80, 65]
    }
    
    df = pd.DataFrame(test_data)
    df.to_csv('test_data.csv', index=False, encoding='utf-8-sig')
    
    # 파일 업로드
    with open('test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 업로드 성공: {result['file_id']}")
        return result['file_id']
    else:
        print(f"❌ 업로드 실패: {response.text}")
        return None

async def monitor_analysis(job_id):
    """WebSocket으로 분석 진행 상황 모니터링"""
    uri = f"ws://localhost:8001/api/v1/ws?job_id={job_id}"
    
    async with websockets.connect(uri) as websocket:
        print(f"🔌 WebSocket 연결: {job_id}")
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("type") == "progress_update":
                print(f"📊 진행률: {data['progress']:.1f}% - {data.get('current_employee', '')}")
            
            elif data.get("type") == "analysis_complete":
                print("✅ 분석 완료!")
                print(f"결과: {json.dumps(data.get('results_summary', {}), indent=2)}")
                break
            
            elif data.get("type") == "error":
                print(f"❌ 오류: {data['error']}")
                break

def start_analysis(file_id):
    """분석 시작"""
    print("\n🚀 분석 시작...")
    
    payload = {
        "file_id": file_id,
        "sample_size": 5,
        "analysis_mode": "hybrid",
        "enable_ai_feedback": False
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 분석 작업 생성: {result['job_id']}")
        return result['job_id']
    else:
        print(f"❌ 분석 시작 실패: {response.text}")
        return None

def check_results(job_id):
    """분석 결과 확인"""
    print("\n📋 결과 확인...")
    
    # 직원 조회
    response = requests.get(f"{BASE_URL}/employee/{job_id}?uid=EMP001")
    if response.status_code == 200:
        result = response.json()
        employee = result.get('employee', {})
        print(f"\n직원 정보 (EMP001):")
        print(f"- UID: {employee.get('uid')}")
        print(f"- 종합점수: {employee.get('hybrid_score')}")
        print(f"- OK등급: {employee.get('ok_grade')}")
        print(f"- 신뢰도: {employee.get('confidence')}%")

async def full_test():
    """전체 테스트 플로우"""
    print("🧪 AIRISS v4.0 WebSocket 전체 테스트 시작\n")
    
    # 1. 파일 업로드
    file_id = upload_test_file()
    if not file_id:
        return
    
    # 2. 분석 시작
    job_id = start_analysis(file_id)
    if not job_id:
        return
    
    # 3. WebSocket으로 진행 상황 모니터링
    await monitor_analysis(job_id)
    
    # 4. 결과 확인
    time.sleep(1)  # 잠시 대기
    check_results(job_id)
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(full_test())