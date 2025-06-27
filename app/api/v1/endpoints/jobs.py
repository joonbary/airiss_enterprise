"""작업 목록 엔드포인트"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.job import JobListResponse, JobInfo
from app.models import Job, FileRecord

router = APIRouter()


@router.get("/jobs", response_model=JobListResponse)
async def get_completed_jobs(
    db: Session = Depends(get_db)
):
    """완료된 분석 작업 목록 조회"""
    try:
        # 완료된 작업 조회
        jobs = db.query(Job).filter(
            Job.status == "completed"
        ).order_by(
            Job.end_time.desc()
        ).all()
        
        job_list = []
        for job in jobs:
            # 파일 정보 조회
            file_record = db.query(FileRecord).filter(
                FileRecord.id == job.file_id
            ).first()
            
            job_info = JobInfo(
                job_id=job.id,
                filename=file_record.filename if file_record else "Unknown",
                processed=job.processed,
                end_time=job.end_time.strftime("%Y-%m-%d %H:%M") if job.end_time else "",
                analysis_mode=job.analysis_mode
            )
            job_list.append(job_info)
        
        return JobListResponse(jobs=job_list)
        
    except Exception as e:
        import logging
        logging.error(f"작업 목록 조회 오류: {e}")
        return JobListResponse(jobs=[])