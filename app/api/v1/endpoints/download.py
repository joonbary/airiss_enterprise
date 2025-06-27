"""결과 다운로드 엔드포인트"""

import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Job

router = APIRouter()


@router.get("/download/{job_id}")
async def download_results(
    job_id: str,
    db: Session = Depends(get_db)
):
    """분석 결과 다운로드"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="아직 완료되지 않은 작업입니다")
    
    result_file = job.result_file_path
    if not result_file or not os.path.exists(result_file):
        raise HTTPException(status_code=404, detail="결과 파일을 찾을 수 없습니다")
    
    # 다운로드용 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ai_suffix = "AI완전분석" if job.enable_ai_feedback else "하이브리드분석"
    analysis_mode = job.analysis_mode or "hybrid"
    filename = f"OK금융그룹_AIRISS_v4.0_{analysis_mode}_{ai_suffix}_{timestamp}.xlsx"
    
    return FileResponse(
        result_file,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename=filename
    )