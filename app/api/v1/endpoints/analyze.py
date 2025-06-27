"""분석 실행 엔드포인트"""

import asyncio
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db, SessionLocal
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.models import Job, FileRecord
from app.services.analysis_service import AnalysisService

router = APIRouter()
logger = logging.getLogger(__name__)

analysis_service = AnalysisService()


@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """분석 작업 시작"""
    try:
        # 파일 존재 확인
        file_record = db.query(FileRecord).filter(FileRecord.id == request.file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # Job 생성
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            file_id=request.file_id,
            status="pending",
            total=0,
            processed=0,
            failed=0,
            progress=0.0,
            sample_size=request.sample_size,
            analysis_mode=request.analysis_mode,
            enable_ai_feedback=request.enable_ai_feedback,
            openai_model=request.openai_model,
            max_tokens=request.max_tokens,
            start_time=datetime.now()
        )
        db.add(job)
        db.commit()
        
        # 백그라운드에서 분석 실행
        asyncio.create_task(
            analysis_service.start_analysis(
                db=SessionLocal(),  # 새 세션 생성
                job_id=job_id,
                file_id=request.file_id,
                sample_size=request.sample_size,
                analysis_mode=request.analysis_mode,
                enable_ai_feedback=request.enable_ai_feedback,
                openai_api_key=request.openai_api_key,
                openai_model=request.openai_model,
                max_tokens=request.max_tokens
            )
        )
        
        logger.info(f"AIRISS v4.0 분석 작업 시작: {job_id}")
        
        return AnalysisResponse(
            job_id=job_id,
            status="started",
            message="OK금융그룹 AIRISS v4.0 하이브리드 분석이 시작되었습니다",
            ai_feedback_enabled=request.enable_ai_feedback,
            analysis_mode=request.analysis_mode
        )
        
    except Exception as e:
        logger.error(f"분석 시작 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))