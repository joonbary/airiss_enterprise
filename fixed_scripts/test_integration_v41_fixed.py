#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.1 통합 테스트 - API 경로 수정 버전
작성일: 2025.01.27
목적: 전체 분석 파이프라인 테스트 (올바른 API 경로 사용)
"""

import asyncio
import aiohttp
import pandas as pd
import json
import os
from datetime import datetime
import numpy as np
from typing import Dict, Any

# 테스트 설정
TEST_SERVER = "http://localhost:8002"

async def test_server_health():
    """서버 상태 확인"""
    print("\n[1] 서버 상태 확인")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 헬스체크
            async with session.get(f"{TEST_SERVER}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 서버 상태: 정상")
                    print(f"   - 버전: {data.get('version', 'unknown')}")
                    print(f"   - 서비스: {data.get('service', 'unknown')}")
                    print(f"   - WebSocket 연결: {data['components'].get('connection_count', 0)}개")
                else:
                    print(f"❌ 서버 상태: 오류 (HTTP {resp.status})")
                    return False
                    
            # DB 상태
            async with session.get(f"{TEST_SERVER}/health/db") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ DB 상태: {data.get('status', 'unknown')}")
                    print(f"   - 파일 수: {data.get('files', 0)}개")
                else:
                    print(f"❌ DB 상태: 오류")
                    
            # 분석 엔진 상태
            async with session.get(f"{TEST_SERVER}/health/analysis") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 분석 엔진: {data.get('status', 'unknown')}")
                    print(f"   - 엔진: {data.get('analysis_engine', 'unknown')}")
                    print(f"   - 차원: {data.get('framework_dimensions', 0)}개")
                    print(f"   - 하이브리드 분석: {data.get('hybrid_analysis', False)}")
                    print(f"   - 편향 탐지: {data.get('bias_detection', False)}")
                else:
                    print(f"❌ 분석 엔진: 오류")
                    
            return True
            
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False

def create_test_data():
    """테스트 데이터 생성"""
    print("\n[2] 테스트 데이터 생성")
    print("-" * 50)
    
    # 다양한 케이스를 포함한 테스트 데이터
    test_cases = []
    
    # 성별, 연령대별로 다양한 케이스 생성
    genders = ['남성', '여성']
    age_groups = ['20대', '30대', '40대', '50대']
    departments = ['영업팀', '개발팀', 'HR팀', '재무팀']
    
    uid = 1000
    for gender in genders:
        for age in age_groups:
            for dept in departments:
                # 각 그룹별로 3명씩 생성
                for i in range(3):
                    # 의도적으로 일부 편향 생성 (테스트용)
                    base_score = 70
                    if gender == '남성' and dept == '개발팀':
                        base_score += 10  # 편향 시뮬레이션
                    if age == '20대':
                        base_score -= 5   # 연령 편향 시뮬레이션
                    
                    opinion = generate_opinion(base_score)
                    
                    test_cases.append({
                        'uid': f'TEST_{uid}',
                        '성별': gender,
                        '연령대': age,
                        '부서': dept,
                        '직급': np.random.choice(['사원', '주임', '대리', '과장']),
                        'opinion': opinion,
                        'kpi_score': np.random.normal(base_score, 10),
                        'attendance_rate': np.random.uniform(90, 100),
                        'project_completion': np.random.uniform(70, 100)
                    })
                    uid += 1
    
    # DataFrame 생성 및 저장
    df = pd.DataFrame(test_cases)
    
    # test_data 폴더 생성
    os.makedirs('test_data', exist_ok=True)
    
    # Excel 파일로 저장
    file_path = 'test_data/airiss_test_data.xlsx'
    df.to_excel(file_path, index=False, engine='openpyxl')
    
    print(f"✅ 테스트 데이터 생성 완료")
    print(f"   - 파일: {file_path}")
    print(f"   - 레코드 수: {len(df)}개")
    print(f"   - 성별 분포: {df['성별'].value_counts().to_dict()}")
    print(f"   - 연령대 분포: {df['연령대'].value_counts().to_dict()}")
    print(f"   - 부서 분포: {df['부서'].value_counts().to_dict()}")
    
    return file_path, df

def generate_opinion(score_level):
    """점수 수준에 따른 의견 생성"""
    if score_level >= 80:
        opinions = [
            "업무 성과가 뛰어나며 목표를 항상 초과 달성합니다. 팀워크도 훌륭하고 리더십을 발휘합니다.",
            "혁신적인 아이디어로 프로세스를 개선했고, 고객 만족도가 크게 향상되었습니다.",
            "전문성이 뛰어나고 동료들에게 멘토링을 제공하며 조직 문화에 긍정적 영향을 미칩니다."
        ]
    elif score_level >= 70:
        opinions = [
            "업무를 성실히 수행하며 목표를 달성합니다. 협업 능력이 좋고 신뢰할 수 있습니다.",
            "꾸준한 성과를 보이며 팀에 기여합니다. 커뮤니케이션 스킬이 양호합니다.",
            "책임감 있게 업무를 처리하며 기한을 준수합니다. 학습 의지가 있습니다."
        ]
    else:
        opinions = [
            "업무 수행에 개선이 필요합니다. 목표 달성률이 저조하며 추가 교육이 필요합니다.",
            "팀워크에 어려움이 있으며 커뮤니케이션 개선이 필요합니다.",
            "업무 집중도가 낮고 동기부여가 필요한 상황입니다."
        ]
    
    return np.random.choice(opinions)

async def test_file_upload(file_path):
    """파일 업로드 테스트"""
    print("\n[3] 파일 업로드 테스트")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 파일 업로드
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file',
                             f,
                             filename='test_data.xlsx',
                             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                
                async with session.post(f"{TEST_SERVER}/api/upload", data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        print(f"✅ 파일 업로드 성공")
                        # 디버깅을 위해 전체 응답 출력
                        print(f"   응답 키: {list(result.keys())[:10]}...")
                        file_id = result.get('id') or result.get('file_id', 'unknown')
                        print(f"   - 파일 ID: {file_id}")
                        print(f"   - 레코드 수: {result.get('total_records', 0)}개")
                        print(f"   - 컬럼: {', '.join(result.get('columns', []))}")
                        return file_id
                    else:
                        print(f"❌ 업로드 실패: HTTP {resp.status}")
                        error_text = await resp.text()
                        print(f"   오류 내용: {error_text}")
                        return None
                        
        except Exception as e:
            print(f"❌ 업로드 오류: {e}")
            return None

async def test_analysis(file_id):
    """분석 실행 테스트 - 올바른 API 경로 사용"""
    print("\n[4] 분석 실행 테스트")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 분석 요청 데이터 준비
            request_data = {
                "file_id": file_id,
                "sample_size": 10,  # 테스트를 위해 10개만
                "analysis_mode": "hybrid",
                "enable_ai_feedback": False
            }
            
            # 올바른 엔드포인트 사용: /api/analysis/start
            print(f"   API 호출: POST {TEST_SERVER}/api/analysis/start")
            print(f"   요청 데이터: {request_data}")
            
            async with session.post(
                f"{TEST_SERVER}/api/analysis/start", 
                json=request_data
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ 분석 시작 성공")
                    print(f"   - 작업 ID: {result.get('job_id', 'unknown')}")
                    print(f"   - 상태: {result.get('status', 'unknown')}")
                    print(f"   - 메시지: {result.get('message', '')}")
                    print(f"   - 예상 시간: {result.get('estimated_time', 'unknown')}")
                    return result.get('job_id')
                else:
                    print(f"❌ 분석 시작 실패: HTTP {resp.status}")
                    error_text = await resp.text()
                    print(f"   오류 내용: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ 분석 오류: {e}")
            return None

async def check_analysis_results(job_id):
    """분석 결과 확인"""
    print("\n[5] 분석 결과 확인")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        max_attempts = 30  # 최대 30초 대기
        
        for attempt in range(max_attempts):
            try:
                # 올바른 상태 확인 경로
                async with session.get(f"{TEST_SERVER}/api/analysis/status/{job_id}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        status = data.get('status', 'unknown')
                        progress = data.get('progress', 0)
                        
                        print(f"\r⏳ 상태: {status}, 진행률: {progress:.1f}%", end='', flush=True)
                        
                        if status == 'completed':
                            print(f"\n✅ 분석 완료!")
                            print(f"   - 처리 시간: {data.get('processing_time', 'unknown')}")
                            print(f"   - 처리 건수: {data.get('processed', 0)}개")
                            print(f"   - 평균 점수: {data.get('average_score', 0)}")
                            
                            # 결과 상세 조회
                            async with session.get(f"{TEST_SERVER}/api/analysis/results/{job_id}") as results_resp:
                                if results_resp.status == 200:
                                    results = await results_resp.json()
                                    analyze_results(results)
                                    
                                    # 편향 분석 결과 확인 (있는 경우)
                                    if 'bias_report' in results:
                                        print("\n📊 편향 분석 결과:")
                                        bias_report = results['bias_report']
                                        print(f"   - 편향 탐지: {bias_report.get('summary', {}).get('bias_detected', 'N/A')}")
                                        print(f"   - 위험 수준: {bias_report.get('summary', {}).get('risk_level', 'N/A')}")
                            
                            return True
                            
                        elif status == 'failed':
                            print(f"\n❌ 분석 실패: {data.get('error', 'unknown error')}")
                            return False
                        
                        # 계속 대기
                        await asyncio.sleep(1)
                        
                    else:
                        print(f"\n❌ 상태 확인 실패: HTTP {resp.status}")
                        return False
                        
            except Exception as e:
                print(f"\n❌ 결과 확인 오류: {e}")
                return False
        
        print("\n❌ 분석 시간 초과 (30초)")
        return False

def analyze_results(results):
    """분석 결과 검토"""
    print("\n📈 분석 결과 요약:")
    print("-" * 50)
    
    if 'results' in results:
        result_list = results['results']
        
        if not result_list:
            print("   결과 데이터가 없습니다.")
            return
            
        df = pd.DataFrame(result_list)
        
        # 전체 통계
        print(f"\n전체 통계:")
        print(f"   - 분석 대상: {len(df)}명")
        
        if 'AIRISS_v4_종합점수' in df.columns:
            print(f"   - 평균 점수: {df['AIRISS_v4_종합점수'].mean():.1f}")
            print(f"   - 표준편차: {df['AIRISS_v4_종합점수'].std():.1f}")
            print(f"   - 최고 점수: {df['AIRISS_v4_종합점수'].max():.1f}")
            print(f"   - 최저 점수: {df['AIRISS_v4_종합점수'].min():.1f}")
        
        # 등급 분포
        if 'OK등급' in df.columns:
            print(f"\n등급 분포:")
            grade_counts = df['OK등급'].value_counts()
            for grade, count in grade_counts.items():
                print(f"   - {grade}: {count}명 ({count/len(df)*100:.1f}%)")

async def test_websocket_connection():
    """WebSocket 연결 테스트"""
    print("\n[6] WebSocket 연결 테스트")
    print("-" * 50)
    
    try:
        import websockets
        
        ws_url = f"ws://localhost:8002/ws/test_client?channels=analysis,alerts"
        
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket 연결 성공")
            
            # 테스트 메시지 전송
            await websocket.send(json.dumps({
                "type": "ping",
                "timestamp": datetime.now().isoformat()
            }))
            
            # 응답 대기 (타임아웃 5초)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"✅ WebSocket 응답: {response}")
            except asyncio.TimeoutError:
                print("⚠️ WebSocket 응답 없음 (정상일 수 있음)")
                
    except Exception as e:
        print(f"❌ WebSocket 연결 실패: {e}")

async def main():
    """메인 테스트 함수"""
    print("=" * 80)
    print("AIRISS v4.1 통합 테스트 시작 (수정된 API 경로)")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. 서버 상태 확인
    if not await test_server_health():
        print("\n❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작하세요:")
        print("   python -m app.main")
        return
    
    # 2. 테스트 데이터 생성
    file_path, test_df = create_test_data()
    
    # 3. 파일 업로드
    file_id = await test_file_upload(file_path)
    if not file_id or file_id == 'unknown':
        print("\n❌ 파일 업로드 실패로 테스트 중단")
        return
    
    # 4. 분석 실행
    job_id = await test_analysis(file_id)
    if not job_id:
        print("\n❌ 분석 시작 실패로 테스트 중단")
        return
    
    # 5. 결과 확인
    await check_analysis_results(job_id)
    
    # 6. WebSocket 테스트
    await test_websocket_connection()
    
    print("\n" + "=" * 80)
    print("테스트 완료!")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
