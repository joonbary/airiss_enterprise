#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.1 빠른 분석 테스트
API 경로를 올바르게 사용하는 간단한 테스트 스크립트
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def quick_test_analysis():
    """빠른 분석 테스트"""
    server_url = "http://localhost:8002"
    
    async with aiohttp.ClientSession() as session:
        # 1. 서버 상태 확인
        print("1. 서버 상태 확인...")
        try:
            async with session.get(f"{server_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ 서버 정상: {data['service']}")
                else:
                    print("❌ 서버 오류")
                    return
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return
        
        # 2. 파일 목록 확인 (이미 업로드된 파일 사용)
        print("\n2. 기존 파일 확인...")
        try:
            async with session.get(f"{server_url}/api/files") as resp:
                if resp.status == 200:
                    files = await resp.json()
                    if files:
                        file_id = files[0]['id']
                        filename = files[0]['filename']
                        print(f"✅ 파일 발견: {filename} (ID: {file_id})")
                    else:
                        print("❌ 업로드된 파일이 없습니다.")
                        return
                else:
                    print("❌ 파일 목록 조회 실패")
                    return
        except Exception as e:
            print(f"❌ 파일 목록 조회 오류: {e}")
            return
        
        # 3. 분석 시작 (올바른 경로 사용)
        print("\n3. 분석 시작...")
        request_data = {
            "file_id": file_id,
            "sample_size": 5,  # 빠른 테스트를 위해 5개만
            "analysis_mode": "hybrid"
        }
        
        try:
            async with session.post(f"{server_url}/api/analysis/start", json=request_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    job_id = result['job_id']
                    print(f"✅ 분석 시작: Job ID = {job_id}")
                else:
                    error_text = await resp.text()
                    print(f"❌ 분석 시작 실패: {resp.status}")
                    print(f"   오류: {error_text}")
                    return
        except Exception as e:
            print(f"❌ 분석 요청 오류: {e}")
            return
        
        # 4. 결과 대기
        print("\n4. 분석 진행 중...")
        for i in range(20):  # 최대 20초 대기
            await asyncio.sleep(1)
            
            try:
                async with session.get(f"{server_url}/api/analysis/status/{job_id}") as resp:
                    if resp.status == 200:
                        status_data = await resp.json()
                        status = status_data['status']
                        progress = status_data.get('progress', 0)
                        
                        if status == 'completed':
                            print(f"\n✅ 분석 완료!")
                            print(f"   - 처리 시간: {status_data.get('processing_time', 'N/A')}")
                            print(f"   - 처리 건수: {status_data.get('processed', 0)}")
                            print(f"   - 평균 점수: {status_data.get('average_score', 0)}")
                            
                            # 결과 조회
                            async with session.get(f"{server_url}/api/analysis/results/{job_id}") as results_resp:
                                if results_resp.status == 200:
                                    results = await results_resp.json()
                                    print(f"\n📊 분석 결과:")
                                    for i, result in enumerate(results['results'][:3]):  # 처음 3개만 출력
                                        print(f"   [{i+1}] UID: {result['UID']}, 점수: {result['AIRISS_v4_종합점수']}, 등급: {result['OK등급']}")
                            
                            return
                        
                        elif status == 'failed':
                            print(f"\n❌ 분석 실패: {status_data.get('error', 'unknown')}")
                            return
                        
                        else:
                            print(f"\r   진행률: {progress:.1f}%", end='', flush=True)
                    
            except Exception as e:
                print(f"\n❌ 상태 확인 오류: {e}")
                return
        
        print("\n❌ 분석 시간 초과")

if __name__ == "__main__":
    print("=" * 60)
    print("AIRISS v4.1 빠른 분석 테스트")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    asyncio.run(quick_test_analysis())
    
    print("\n테스트 완료!")
