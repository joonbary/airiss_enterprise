#!/usr/bin/env python3
"""
AIRISS 데이터베이스 상태 확인 스크립트
현재 데이터베이스에 어떤 jobs와 results가 있는지 확인
"""

import asyncio
import sys
import os

# AIRISS 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.sqlite_service import SQLiteService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_database_status():
    """데이터베이스 상태 확인"""
    
    print("=" * 60)
    print("🔍 AIRISS 데이터베이스 상태 확인")
    print("=" * 60)
    
    try:
        # SQLiteService 인스턴스 생성
        sqlite_service = SQLiteService()
        
        # 1. 데이터베이스 초기화 확인
        await sqlite_service.init_database()
        print("✅ 데이터베이스 초기화 성공")
        
        # 2. 파일 목록 확인
        files = await sqlite_service.list_files()
        print(f"\n📁 업로드된 파일 수: {len(files)}")
        for file in files[:5]:  # 최근 5개만 표시
            print(f"   - {file['filename']} (ID: {file['id'][:8]}...)")
        
        # 3. 작업 목록 확인
        jobs = await sqlite_service.list_jobs()
        print(f"\n📋 분석 작업 수: {len(jobs)}")
        for job in jobs[:10]:  # 최근 10개만 표시
            print(f"   - Job ID: {job['id'][:8]}... | Status: {job['status']} | Records: {job.get('total_records', 0)}")
        
        # 4. 완료된 작업들 확인
        completed_jobs = await sqlite_service.get_completed_analysis_jobs()
        print(f"\n✅ 완료된 작업 수: {len(completed_jobs)}")
        
        if completed_jobs:
            print("\n📊 완료된 작업 상세:")
            for job in completed_jobs[:5]:
                job_id = job['job_id']
                print(f"\n   🎯 Job ID: {job_id}")
                print(f"      파일명: {job.get('filename', 'N/A')}")
                print(f"      상태: {job['status']}")
                print(f"      처리된 레코드: {job.get('processed_records', 0)}")
                
                # 해당 작업의 결과 확인
                results = await sqlite_service.get_analysis_results(job_id)
                print(f"      분석 결과 수: {len(results)}")
                
                if results:
                    # 첫 번째 결과 샘플 확인
                    first_result = results[0]
                    print(f"      샘플 UID: {first_result['uid']}")
                    result_data = first_result['result_data']
                    if isinstance(result_data, dict):
                        print(f"      샘플 점수: {result_data.get('AIRISS_v2_종합점수', 'N/A')}")
                        print(f"      샘플 등급: {result_data.get('OK등급', 'N/A')}")
                
                print()
        
        # 5. 특정 job_id 확인 (스크린샷에서 오류가 발생한 것)
        problem_job_id = "ab4f35d3-ce09-4607-bf4f-e44ec0ac3f7e"
        print(f"🔍 문제 job_id 확인: {problem_job_id}")
        
        problem_job = await sqlite_service.get_analysis_job(problem_job_id)
        if problem_job:
            print(f"   ✅ Job 존재: {problem_job['status']}")
            
            problem_results = await sqlite_service.get_analysis_results(problem_job_id)
            print(f"   📊 결과 수: {len(problem_results)}")
            
            if problem_results:
                print("   🎯 사용 가능한 UID들:")
                for result in problem_results[:10]:
                    print(f"      - {result['uid']}")
        else:
            print(f"   ❌ Job 없음: {problem_job_id}")
        
        # 6. 데이터베이스 통계
        stats = await sqlite_service.get_database_stats()
        print(f"\n📈 데이터베이스 통계:")
        print(f"   - 파일: {stats.get('files_count', 0)}개")
        print(f"   - 작업: {stats.get('jobs_count', 0)}개") 
        print(f"   - 결과: {stats.get('results_count', 0)}개")
        print(f"   - DB 경로: {stats.get('db_path', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(check_database_status())
