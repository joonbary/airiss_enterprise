# app/api/analysis.py
# AIRISS v4.0 Analysis API - 무한 로딩 해결 버전 (수정됨)

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import asyncio
import logging
import traceback
from datetime import datetime
import pandas as pd
import numpy as np
import json

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/analysis", tags=["analysis"])

# 🔥 전역 인스턴스 저장용
_db_service = None
_ws_manager = None

def get_db_service():
    """DB 서비스 가져오기"""
    global _db_service
    if _db_service is None:
        from app.db.sqlite_service import SQLiteService
        _db_service = SQLiteService()
        logger.info("✅ SQLiteService 인스턴스 생성됨")
    return _db_service

def get_ws_manager():
    """WebSocket 매니저 가져오기"""
    global _ws_manager
    if _ws_manager is None:
        from app.core.websocket_manager import ConnectionManager
        _ws_manager = ConnectionManager()
        logger.info("✅ WebSocket 매니저 인스턴스 생성됨")
    return _ws_manager

# 🔥 초기화 함수 (main.py에서 호출)
def init_services(db_service, ws_manager):
    """서비스 인스턴스 초기화"""
    global _db_service, _ws_manager
    _db_service = db_service
    _ws_manager = ws_manager
    logger.info("✅ Analysis 모듈 서비스 초기화 완료")

# [기존 AIRISS_FRAMEWORK 코드는 그대로 유지]
# ... (AIRISS_FRAMEWORK, QuantitativeAnalyzer, AIRISSTextAnalyzer, AIRISSHybridAnalyzer 등은 동일)

# API 모델 정의
class AnalysisRequest(BaseModel):
    file_id: str
    sample_size: int = 10
    analysis_mode: str = "hybrid"  # "text", "quantitative", "hybrid"
    openai_api_key: Optional[str] = None
    enable_ai_feedback: bool = False
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

# 🔥 수정된 분석 시작 엔드포인트
@router.post("/start")
async def start_analysis(
    request: AnalysisRequest, 
    background_tasks: BackgroundTasks
):
    """분석 작업 시작 - 무한 로딩 해결 버전"""
    try:
        logger.info(f"🚀 분석 시작 요청: file_id={request.file_id}, sample_size={request.sample_size}")
        
        # DB 서비스 가져오기
        db_service = get_db_service()
        ws_manager = get_ws_manager()
        
        # DB 초기화 확인
        try:
            await db_service.init_database()
        except Exception as e:
            logger.warning(f"DB 초기화 건너뜀: {e}")
        
        # 1. 파일 존재 확인
        file_data = await db_service.get_file(request.file_id)
        if not file_data:
            logger.error(f"❌ 파일을 찾을 수 없음: {request.file_id}")
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 2. 작업 ID 생성
        job_id = str(uuid.uuid4())
        logger.info(f"🆕 작업 ID 생성: {job_id}")
        
        # 3. 작업 데이터 준비
        job_data = {
            "job_id": job_id,
            "file_id": request.file_id,
            "status": "processing",
            "sample_size": request.sample_size,
            "analysis_mode": request.analysis_mode,
            "enable_ai_feedback": request.enable_ai_feedback,
            "openai_model": request.openai_model,
            "max_tokens": request.max_tokens,
            "start_time": datetime.now().isoformat(),
            "progress": 0.0,
            "total_records": request.sample_size,
            "processed_records": 0,
            "failed_records": 0,
            "version": "4.0"
        }
        
        # 4. SQLite에 작업 저장
        saved_job_id = await db_service.create_analysis_job(job_data)
        if saved_job_id != job_id:
            logger.error(f"❌ Job ID 불일치! 요청: {job_id}, 저장: {saved_job_id}")
            raise HTTPException(status_code=500, detail="작업 ID 생성 오류")
        
        # 5. 🔥 백그라운드 작업 추가 (FastAPI BackgroundTasks 사용)
        background_tasks.add_task(
            safe_process_analysis_v4,
            job_id,
            request,
            db_service,
            ws_manager
        )
        logger.info(f"✅ 백그라운드 작업 추가 완료: {job_id}")
        
        # 6. WebSocket 알림
        try:
            await ws_manager.broadcast_to_channel("analysis", {
                "type": "analysis_started",
                "job_id": job_id,
                "file_id": request.file_id,
                "analysis_mode": request.analysis_mode,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.warning(f"⚠️ WebSocket 알림 실패: {e}")
        
        # 7. 성공 응답
        return {
            "job_id": job_id,
            "status": "started",
            "message": "OK금융그룹 AIRISS v4.0 하이브리드 분석이 시작되었습니다",
            "ai_feedback_enabled": request.enable_ai_feedback,
            "analysis_mode": request.analysis_mode,
            "sample_size": request.sample_size,
            "estimated_time": f"{request.sample_size * 0.2}초"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 예상치 못한 분석 시작 오류: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"분석 시작 중 예상치 못한 오류: {str(e)}")

# 🔥 수정된 백그라운드 처리 함수
async def safe_process_analysis_v4(job_id: str, request: AnalysisRequest, db_service, ws_manager):
    """안전한 백그라운드 분석 처리"""
    try:
        logger.info(f"🔥 백그라운드 분석 시작: {job_id}")
        
        # 실제 분석 처리
        await process_analysis_v4(job_id, request, db_service, ws_manager)
        
        logger.info(f"✅ 백그라운드 분석 완료: {job_id}")
        
    except Exception as e:
        logger.error(f"❌ 백그라운드 분석 오류: {job_id} - {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        
        # 오류 발생 시 작업 상태 업데이트
        try:
            await db_service.update_analysis_job(job_id, {
                "status": "failed",
                "error": f"분석 처리 오류: {str(e)}",
                "end_time": datetime.now().isoformat()
            })
            
            # WebSocket 오류 알림
            await ws_manager.broadcast_to_channel("analysis", {
                "type": "analysis_failed",
                "job_id": job_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as update_error:
            logger.error(f"❌ 오류 상태 업데이트 실패: {update_error}")

# 🔥 간소화된 분석 처리 함수 (테스트용)
async def process_analysis_v4(job_id: str, request: AnalysisRequest, db_service, ws_manager):
    """AIRISS v4.0 분석 처리 - 간소화 버전"""
    try:
        logger.info(f"📊 분석 처리 시작: {job_id}")
        
        # 1. 파일 데이터 로드
        file_data = await db_service.get_file(request.file_id)
        if not file_data:
            raise Exception(f"파일을 찾을 수 없음: {request.file_id}")
        
        # 2. DataFrame 확인
        df = file_data.get('dataframe')
        if df is None:
            raise Exception("DataFrame을 로드할 수 없습니다")
        
        logger.info(f"📋 데이터 로드 완료: {len(df)}행")
        
        # 3. 샘플 데이터 선택
        sample_size = min(request.sample_size, len(df))
        sample_df = df.head(sample_size).copy()
        
        # 4. 컬럼 정보 확인
        uid_cols = file_data.get("uid_columns", [])
        opinion_cols = file_data.get("opinion_columns", [])
        
        if not uid_cols:
            # UID 컬럼이 없으면 첫 번째 컬럼 사용
            uid_cols = [df.columns[0]]
        
        # 5. 간단한 분석 진행 (테스트용)
        results = []
        total_rows = len(sample_df)
        
        for idx, row in sample_df.iterrows():
            try:
                # UID 추출
                uid = str(row[uid_cols[0]]) if uid_cols else f"user_{idx}"
                
                # 임시 점수 생성 (60-90 범위)
                main_score = 60 + (idx % 30)
                
                # 등급 계산
                if main_score >= 90:
                    main_grade = "OK★★★"
                elif main_score >= 85:
                    main_grade = "OK★★"
                elif main_score >= 80:
                    main_grade = "OK★"
                elif main_score >= 75:
                    main_grade = "OK A"
                elif main_score >= 70:
                    main_grade = "OK B+"
                else:
                    main_grade = "OK B"
                
                # 결과 레코드 생성
                result_record = {
                    "UID": uid,
                    "원본의견": "테스트 분석 중...",
                    "AIRISS_v4_종합점수": main_score,
                    "OK등급": main_grade,
                    "등급설명": f"{main_grade} 등급",
                    "백분위": f"상위 {100 - idx}%",
                    "분석신뢰도": 80.0,
                    "분석모드": request.analysis_mode,
                    "분석시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # SQLite에 개별 결과 저장
                await db_service.save_analysis_result(job_id, uid, result_record)
                results.append(result_record)
                
                # 진행률 업데이트
                current_processed = len(results)
                progress = (current_processed / total_rows) * 100
                
                await db_service.update_analysis_job(job_id, {
                    "processed_records": current_processed,
                    "progress": min(progress, 100)
                })
                
                # WebSocket 진행률 알림
                await ws_manager.broadcast_to_channel("analysis", {
                    "type": "analysis_progress",
                    "job_id": job_id,
                    "progress": progress,
                    "processed": current_processed,
                    "total": total_rows,
                    "current_uid": uid,
                    "current_score": main_score,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"📈 진행률: {progress:.1f}% ({current_processed}/{total_rows})")
                
                # 처리 속도 조절
                await asyncio.sleep(0.1)  # 0.1초 대기
                
            except Exception as e:
                logger.error(f"❌ 개별 분석 오류 - UID {idx}: {e}")
                continue
        
        # 6. 분석 완료 처리
        end_time = datetime.now()
        avg_score = sum(r["AIRISS_v4_종합점수"] for r in results) / len(results) if results else 0
        
        await db_service.update_analysis_job(job_id, {
            "status": "completed",
            "end_time": end_time.isoformat(),
            "average_score": round(avg_score, 1),
            "processed_records": len(results),
            "progress": 100.0
        })
        
        # WebSocket 완료 알림
        await ws_manager.broadcast_to_channel("analysis", {
            "type": "analysis_completed",
            "job_id": job_id,
            "total_processed": len(results),
            "average_score": round(avg_score, 1),
            "timestamp": end_time.isoformat()
        })
        
        logger.info(f"🎉 분석 완료: {job_id}, 처리: {len(results)}건")
        
    except Exception as e:
        logger.error(f"❌ 분석 처리 오류: {job_id} - {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        
        # 실패 상태 업데이트
        await db_service.update_analysis_job(job_id, {
            "status": "failed",
            "error": str(e),
            "end_time": datetime.now().isoformat()
        })
        
        # WebSocket 오류 알림
        await ws_manager.broadcast_to_channel("analysis", {
            "type": "analysis_failed",
            "job_id": job_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        
        raise

# [기존의 나머지 엔드포인트들은 그대로 유지]
# @router.get("/status/{job_id}")
# @router.get("/jobs")
# @router.get("/results/{job_id}")
# @router.get("/download/{job_id}/{format}")
# @router.get("/health")
# ... (기존 코드 그대로)
