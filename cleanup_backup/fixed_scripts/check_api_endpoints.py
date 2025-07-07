#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.1 API 엔드포인트 확인 스크립트
모든 API 경로를 확인하고 테스트
"""

import asyncio
import aiohttp
from datetime import datetime

async def check_all_endpoints():
    """모든 API 엔드포인트 확인"""
    server_url = "http://localhost:8002"
    
    # 테스트할 엔드포인트 목록
    endpoints = [
        # 기본 엔드포인트
        {"method": "GET", "path": "/", "description": "메인 페이지"},
        {"method": "GET", "path": "/api", "description": "API 정보"},
        {"method": "GET", "path": "/health", "description": "서버 헬스체크"},
        {"method": "GET", "path": "/health/db", "description": "DB 헬스체크"},
        {"method": "GET", "path": "/health/analysis", "description": "분석 엔진 헬스체크"},
        {"method": "GET", "path": "/dashboard", "description": "개발자 대시보드"},
        
        # 파일 관련 API
        {"method": "GET", "path": "/api/files", "description": "파일 목록"},
        {"method": "POST", "path": "/api/upload", "description": "파일 업로드"},
        
        # 분석 관련 API (올바른 경로)
        {"method": "POST", "path": "/api/analysis/start", "description": "분석 시작"},
        {"method": "GET", "path": "/api/analysis/status/{job_id}", "description": "분석 상태"},
        {"method": "GET", "path": "/api/analysis/results/{job_id}", "description": "분석 결과"},
        {"method": "GET", "path": "/api/analysis/jobs", "description": "작업 목록"},
        {"method": "GET", "path": "/api/analysis/health", "description": "분석 엔진 헬스"},
        
        # 잘못된 경로 (테스트에서 사용했던 것)
        {"method": "POST", "path": "/api/analyze/{file_id}", "description": "❌ 잘못된 경로"},
    ]
    
    async with aiohttp.ClientSession() as session:
        print("=" * 70)
        print(f"AIRISS v4.1 API 엔드포인트 확인 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print(f"서버 URL: {server_url}")
        print("-" * 70)
        print(f"{'Method':<8} {'Path':<35} {'Status':<8} {'Description'}")
        print("-" * 70)
        
        for endpoint in endpoints:
            method = endpoint["method"]
            path = endpoint["path"]
            description = endpoint["description"]
            
            # {job_id} 같은 파라미터가 있는 경우 테스트용 값으로 대체
            test_path = path.replace("{job_id}", "test-job-id")
            test_path = test_path.replace("{file_id}", "test-file-id")
            
            try:
                if method == "GET":
                    async with session.get(f"{server_url}{test_path}") as resp:
                        status = resp.status
                        status_icon = "✅" if status == 200 else "❌"
                        print(f"{method:<8} {path:<35} {status:<8} {status_icon} {description}")
                        
                elif method == "POST":
                    # POST 요청은 실제로 보내지 않고 OPTIONS로 확인
                    async with session.options(f"{server_url}{test_path}") as resp:
                        # OPTIONS가 지원되지 않으면 HEAD 시도
                        if resp.status == 405:
                            async with session.head(f"{server_url}{test_path}") as head_resp:
                                status = "POST"
                                status_icon = "🔵"
                        else:
                            status = resp.status
                            status_icon = "🔵" if status < 400 else "❌"
                        print(f"{method:<8} {path:<35} {status:<8} {status_icon} {description}")
                        
            except Exception as e:
                print(f"{method:<8} {path:<35} ERROR    ❌ {description} - {str(e)[:30]}")
        
        print("-" * 70)
        
        # API 문서 확인
        print("\n📚 API 문서:")
        try:
            async with session.get(f"{server_url}/docs") as resp:
                if resp.status == 200:
                    print(f"   ✅ Swagger UI: {server_url}/docs")
                else:
                    print(f"   ❌ Swagger UI 접근 불가")
        except:
            print(f"   ❌ Swagger UI 확인 실패")
            
        try:
            async with session.get(f"{server_url}/redoc") as resp:
                if resp.status == 200:
                    print(f"   ✅ ReDoc: {server_url}/redoc")
                else:
                    print(f"   ❌ ReDoc 접근 불가")
        except:
            print(f"   ❌ ReDoc 확인 실패")

async def test_correct_analysis_flow():
    """올바른 분석 플로우 테스트"""
    print("\n" + "=" * 70)
    print("올바른 분석 플로우 예시")
    print("=" * 70)
    
    print("""
1. 파일 업로드:
   POST /api/upload
   → 응답: {"id": "file-uuid", "filename": "test.xlsx", ...}

2. 분석 시작:
   POST /api/analysis/start
   → 요청: {
       "file_id": "file-uuid",
       "sample_size": 10,
       "analysis_mode": "hybrid"
     }
   → 응답: {"job_id": "job-uuid", "status": "started", ...}

3. 상태 확인:
   GET /api/analysis/status/{job_id}
   → 응답: {"status": "processing", "progress": 50.0, ...}

4. 결과 조회:
   GET /api/analysis/results/{job_id}
   → 응답: {"results": [...], "total_count": 10, ...}

5. 결과 다운로드:
   GET /api/analysis/download/{job_id}/excel
   → Excel 파일 다운로드
""")

if __name__ == "__main__":
    asyncio.run(check_all_endpoints())
    asyncio.run(test_correct_analysis_flow())
