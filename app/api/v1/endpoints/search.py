# C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\app\api\v1\endpoints\search.py
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.db.database import get_db
from app.models.domain import EmployeeScore, AnalysisJob

router = APIRouter()

@router.get("/employee/{job_id}")
async def search_employee(
    job_id: str,
    uid: Optional[str] = Query(None, description="직원 UID"),
    grade: Optional[str] = Query(None, description="OK등급 필터"),
    db: Session = Depends(get_db)
):
    """개별 직원 검색"""
    # 작업 확인
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    # 쿼리 작성
    query = db.query(EmployeeScore).filter(EmployeeScore.job_id == job_id)
    
    if uid:
        query = query.filter(EmployeeScore.uid == uid)
    if grade:
        query = query.filter(EmployeeScore.ok_grade == grade)
    
    # 결과 조회
    employee = query.first()
    
    if not employee:
        raise HTTPException(status_code=404, detail="직원을 찾을 수 없습니다")
    
    # 전체 통계 계산
    all_scores = db.query(EmployeeScore).filter(EmployeeScore.job_id == job_id).all()
    
    avg_hybrid = sum(s.hybrid_score for s in all_scores) / len(all_scores)
    avg_text = sum(s.text_score for s in all_scores) / len(all_scores)
    avg_quant = sum(s.quantitative_score for s in all_scores) / len(all_scores)
    
    return {
        "employee": {
            "uid": employee.uid,
            "hybrid_score": employee.hybrid_score,
            "text_score": employee.text_score,
            "quantitative_score": employee.quantitative_score,
            "ok_grade": employee.ok_grade,
            "percentile": employee.percentile
        },
        "statistics": {
            "total_count": len(all_scores),
            "average_scores": {
                "hybrid_avg": round(avg_hybrid, 1),
                "text_avg": round(avg_text, 1),
                "quant_avg": round(avg_quant, 1)
            }
        }
    }

@router.get("/jobs")
async def get_completed_jobs(db: Session = Depends(get_db)):
    """완료된 작업 목록"""
    jobs = db.query(AnalysisJob).filter(
        AnalysisJob.status == "completed"
    ).order_by(AnalysisJob.end_time.desc()).all()
    
    return [
        {
            "job_id": job.id,
            "filename": "분석 파일",  # FileUpload 조인 필요
            "processed": job.processed_count,
            "end_time": job.end_time.isoformat() if job.end_time else None
        }
        for job in jobs
    ]