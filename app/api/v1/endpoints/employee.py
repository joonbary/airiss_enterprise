"""직원 조회 엔드포인트"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.schemas.employee import EmployeeSearchResponse, EmployeeListResponse
from app.models import Job, EmployeeResult

router = APIRouter()


@router.get("/employee/{job_id}", response_model=EmployeeSearchResponse)
async def search_employee(
    job_id: str,
    uid: Optional[str] = Query(None, description="직원 UID"),
    grade: Optional[str] = Query(None, description="OK등급 필터"),
    db: Session = Depends(get_db)
):
    """개별 직원 데이터 검색 - 전체 평균 및 통계 포함"""
    try:
        # Job 확인
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or job.status != "completed":
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        # 전체 통계 계산
        results_query = db.query(EmployeeResult).filter(EmployeeResult.job_id == job_id)
        total_count = results_query.count()
        
        if total_count == 0:
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        # 평균 점수 계산
        avg_scores = {
            "hybrid_avg": round(db.query(func.avg(EmployeeResult.hybrid_score))
                               .filter(EmployeeResult.job_id == job_id).scalar() or 0, 1),
            "text_avg": round(db.query(func.avg(EmployeeResult.text_total_score))
                             .filter(EmployeeResult.job_id == job_id).scalar() or 0, 1),
            "quant_avg": round(db.query(func.avg(EmployeeResult.quant_total_score))
                              .filter(EmployeeResult.job_id == job_id).scalar() or 0, 1),
            "confidence_avg": round(db.query(func.avg(EmployeeResult.analysis_confidence))
                                   .filter(EmployeeResult.job_id == job_id).scalar() or 0, 1)
        }
        
        # 8대 영역별 평균 (dimension_scores가 문자열로 저장되어 있으므로 별도 계산 필요)
        dimension_avgs = self._calculate_dimension_averages(results_query.all())
        
        # 등급 분포
        grade_counts = db.query(
            EmployeeResult.ok_grade,
            func.count(EmployeeResult.ok_grade)
        ).filter(
            EmployeeResult.job_id == job_id
        ).group_by(EmployeeResult.ok_grade).all()
        
        grade_distribution = {grade: count for grade, count in grade_counts}
        
        # 최고 등급 비율 계산
        top_grades = ["OK★★★", "OK★★", "OK★"]
        top_grade_count = sum(grade_distribution.get(g, 0) for g in top_grades)
        top_grade_ratio = round((top_grade_count / total_count) * 100, 1) if total_count > 0 else 0
        
        # 직원 검색
        employee_data = None
        
        if uid:
            employee = results_query.filter(EmployeeResult.uid == uid).first()
            if employee:
                employee_data = self._employee_to_dict(employee, avg_scores, total_count, results_query)
        
        if grade and not employee_data:
            employee = results_query.filter(EmployeeResult.ok_grade == grade).first()
            if employee:
                employee_data = self._employee_to_dict(employee, avg_scores, total_count, results_query)
        
        if not employee_data:
            # 첫 번째 결과 반환
            employee = results_query.first()
            employee_data = self._employee_to_dict(employee, avg_scores, total_count, results_query)
        
        return EmployeeSearchResponse(
            employee=employee_data,
            statistics={
                "total_count": total_count,
                "average_scores": avg_scores,
                "dimension_averages": dimension_avgs,
                "grade_distribution": grade_distribution,
                "top_grade_ratio": top_grade_ratio
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"직원 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")


@router.get("/employees/{job_id}", response_model=EmployeeListResponse)
async def get_employees_list(
    job_id: str,
    limit: int = Query(50, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """직원 목록 조회 (자동완성용)"""
    try:
        # Job 확인
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or job.status != "completed":
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        # 직원 목록 조회
        employees = db.query(
            EmployeeResult.uid,
            EmployeeResult.ok_grade,
            EmployeeResult.hybrid_score
        ).filter(
            EmployeeResult.job_id == job_id
        ).order_by(
            EmployeeResult.hybrid_score.desc()
        ).limit(limit).all()
        
        employee_list = [
            {
                "uid": emp.uid,
                "grade": emp.ok_grade,
                "score": emp.hybrid_score
            }
            for emp in employees
        ]
        
        return EmployeeListResponse(employees=employee_list)
        
    except Exception as e:
        import logging
        logging.error(f"직원 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="목록 조회 실패")


def _calculate_dimension_averages(employees):
    """8대 영역별 평균 계산"""
    from app.core.analyzers.framework import AIRISS_FRAMEWORK
    
    dimension_sums = {dim: 0 for dim in AIRISS_FRAMEWORK.keys()}
    dimension_counts = {dim: 0 for dim in AIRISS_FRAMEWORK.keys()}
    
    for employee in employees:
        try:
            dim_scores = eval(employee.dimension_scores or "{}")
            for dim, score in dim_scores.items():
                if dim in dimension_sums:
                    dimension_sums[dim] += score
                    dimension_counts[dim] += 1
        except:
            continue
    
    dimension_avgs = {}
    for dim in AIRISS_FRAMEWORK.keys():
        if dimension_counts[dim] > 0:
            dimension_avgs[dim] = round(dimension_sums[dim] / dimension_counts[dim], 1)
        else:
            dimension_avgs[dim] = 50.0
    
    return dimension_avgs


def _employee_to_dict(employee, avg_scores, total_count, results_query):
    """직원 엔티티를 딕셔너리로 변환"""
    # 백분위 계산
    higher_count = results_query.filter(
        EmployeeResult.hybrid_score > employee.hybrid_score
    ).count()
    percentile_rank = round(((total_count - higher_count) / total_count) * 100, 1)
    
    # 점수 차이 계산
    score_differences = {
        "hybrid_diff": round(employee.hybrid_score - avg_scores["hybrid_avg"], 1),
        "text_diff": round(employee.text_total_score - avg_scores["text_avg"], 1),
        "quant_diff": round(employee.quant_total_score - avg_scores["quant_avg"], 1),
        "confidence_diff": round(employee.analysis_confidence - avg_scores["confidence_avg"], 1)
    }
    
    # dimension_scores 파싱
    dimension_scores = {}
    try:
        dimension_scores = eval(employee.dimension_scores or "{}")
    except:
        pass
    
    # 8대 영역별 점수 추가
    dimension_text_scores = {}
    for dim in dimension_scores.keys():
        dimension_text_scores[f"{dim}_텍스트점수"] = dimension_scores[dim]
    
    return {
        "UID": employee.uid,
        "원본의견": employee.original_opinion,
        "AIRISS_v2_종합점수": employee.hybrid_score,
        "OK등급": employee.ok_grade,
        "등급설명": employee.grade_description,
        "백분위": employee.percentile,
        "분석신뢰도": employee.analysis_confidence,
        "텍스트_종합점수": employee.text_total_score,
        "정량_종합점수": employee.quant_total_score,
        "정량_데이터품질": employee.quant_data_quality,
        "AI_장점": employee.ai_strengths,
        "AI_개선점": employee.ai_weaknesses,
        "AI_종합피드백": employee.ai_feedback,
        "percentile_rank": percentile_rank,
        "score_differences": score_differences,
        **dimension_text_scores
    }