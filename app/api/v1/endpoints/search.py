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
    """개별 직원 검색 - UID 또는 등급 필터 (OR 조건)"""
    # 작업 확인
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    # 기본 쿼리
    base_query = db.query(EmployeeScore).filter(EmployeeScore.job_id == job_id)
    
    # 검색 조건 처리 (OR 로직)
    employee = None
    
    if uid and grade:
        # 둘 다 있으면 UID 우선 검색
        employee = base_query.filter(EmployeeScore.uid == uid).first()
        if not employee:
            # UID로 못 찾으면 등급으로 검색
            employee = base_query.filter(EmployeeScore.ok_grade == grade).first()
    elif uid:
        # UID만 있는 경우
        employee = base_query.filter(EmployeeScore.uid == uid).first()
    elif grade:
        # 등급만 있는 경우
        employee = base_query.filter(EmployeeScore.ok_grade == grade).first()
    else:
        # 둘 다 없으면 첫 번째 직원 반환 (또는 에러)
        employee = base_query.first()
        if not employee:
            raise HTTPException(status_code=404, detail="검색 조건을 입력하거나 해당 작업에 데이터가 있는지 확인해주세요")
    
    if not employee:
        search_info = f"UID: {uid}" if uid else f"등급: {grade}" if grade else "조건 없음"
        raise HTTPException(status_code=404, detail=f"검색 조건({search_info})에 해당하는 직원을 찾을 수 없습니다")
    
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