"""분석 상태 확인 엔드포인트"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.status import StatusResponse
from app.models import Job

router = APIRouter()


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_analysis_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """분석 진행 상황 확인"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    # 처리 시간 계산
    if job.status == "completed" and job.end_time:
        processing_time = job.end_time - job.start_time
    else:
        from datetime import datetime
        processing_time = datetime.now() - job.start_time
    
    minutes = int(processing_time.total_seconds() // 60)
    seconds = int(processing_time.total_seconds() % 60)
    time_str = f"{minutes}분 {seconds}초" if minutes > 0 else f"{seconds}초"
    
    # 하이브리드 분석 정보 파싱
    hybrid_info = {}
    if job.hybrid_analysis_info:
        try:
            hybrid_info = eval(job.hybrid_analysis_info)
        except:
            pass
    
    return StatusResponse(
        job_id=job_id,
        status=job.status,
        total=job.total,
        processed=job.processed,
        failed=job.failed,
        progress=job.progress,
        processing_time=time_str,
        average_score=job.average_score or 0,
        error=job.error_message or "",
        ai_success_count=job.ai_success_count or 0,
        ai_fail_count=job.ai_fail_count or 0,
        version="4.0",
        hybrid_analysis_info=hybrid_info
    )