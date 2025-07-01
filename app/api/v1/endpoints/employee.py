"""직원 조회 엔드포인트 - SQLiteService 호환 버전"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.sqlite_service import SQLiteService
from app.schemas.employee import EmployeeSearchResponse, EmployeeListResponse
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# SQLiteService 인스턴스 생성
async def get_sqlite_service():
    return SQLiteService()


@router.get("/employee/{job_id}", response_model=EmployeeSearchResponse)
async def search_employee(
    job_id: str,
    uid: Optional[str] = Query(None, description="직원 UID"),
    grade: Optional[str] = Query(None, description="OK등급 필터"),
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """개별 직원 데이터 검색 - SQLiteService 호환"""
    try:
        logger.info(f"🔍 직원 검색 요청: job_id={job_id}, uid={uid}, grade={grade}")
        
        # 1. Job 확인
        job = await sqlite_service.get_analysis_job(job_id)
        if not job or job.get('status') != 'completed':
            logger.warning(f"완료된 작업을 찾을 수 없음: {job_id}")
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        # 2. 모든 결과 조회
        all_results = await sqlite_service.get_analysis_results(job_id)
        if not all_results:
            logger.warning(f"분석 결과가 없음: {job_id}")
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        logger.info(f"📊 총 결과 수: {len(all_results)}")
        
        # 3. 직원 검색 (OR 로직)
        target_employee = None
        
        if uid and grade:
            # 둘 다 있으면 UID 우선 검색
            target_employee = next((r for r in all_results if r['uid'] == uid), None)
            if not target_employee:
                # UID로 못 찾으면 등급으로 검색
                target_employee = next((r for r in all_results if r['result_data'].get('OK등급') == grade), None)
        elif uid:
            # UID만 있는 경우
            target_employee = next((r for r in all_results if r['uid'] == uid), None)
        elif grade:
            # 등급만 있는 경우
            target_employee = next((r for r in all_results if r['result_data'].get('OK등급') == grade), None)
        else:
            # 둘 다 없으면 첫 번째 직원 반환
            target_employee = all_results[0] if all_results else None
        
        if not target_employee:
            search_info = f"UID: {uid}" if uid else f"등급: {grade}" if grade else "조건 없음"
            logger.warning(f"검색 조건에 맞는 직원 없음: {search_info}")
            raise HTTPException(
                status_code=404, 
                detail=f"검색 조건({search_info})에 해당하는 직원을 찾을 수 없습니다"
            )
        
        # 4. 통계 계산
        hybrid_scores = []
        text_scores = []
        quant_scores = []
        confidence_scores = []
        grade_counts = {}
        
        for result in all_results:
            result_data = result['result_data']
            hybrid_scores.append(result_data.get('AIRISS_v2_종합점수', 0))
            text_scores.append(result_data.get('텍스트_종합점수', 0))
            quant_scores.append(result_data.get('정량_종합점수', 0))
            confidence_scores.append(result_data.get('분석신뢰도', 0))
            
            grade = result_data.get('OK등급', 'N/A')
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # 평균 계산
        total_count = len(all_results)
        avg_scores = {
            "hybrid_avg": round(sum(hybrid_scores) / total_count, 1),
            "text_avg": round(sum(text_scores) / total_count, 1),
            "quant_avg": round(sum(quant_scores) / total_count, 1),
            "confidence_avg": round(sum(confidence_scores) / total_count, 1)
        }
        
        # 최고 등급 비율
        top_grades = ["OK★★★", "OK★★", "OK★"]
        top_grade_count = sum(grade_counts.get(g, 0) for g in top_grades)
        top_grade_ratio = round((top_grade_count / total_count) * 100, 1) if total_count > 0 else 0
        
        # 5. 직원 데이터 구성
        employee_data = target_employee['result_data']
        
        # 백분위 계산
        current_score = employee_data.get('AIRISS_v2_종합점수', 0)
        higher_count = sum(1 for s in hybrid_scores if s > current_score)
        percentile_rank = round(((total_count - higher_count) / total_count) * 100, 1)
        
        # 차이 계산
        score_differences = {
            "hybrid_diff": round(current_score - avg_scores["hybrid_avg"], 1),
            "text_diff": round(employee_data.get('텍스트_종합점수', 0) - avg_scores["text_avg"], 1),
            "quant_diff": round(employee_data.get('정량_종합점수', 0) - avg_scores["quant_avg"], 1),
            "confidence_diff": round(employee_data.get('분석신뢰도', 0) - avg_scores["confidence_avg"], 1)
        }
        
        # 최종 응답 데이터 구성
        response_employee_data = {
            **employee_data,  # 기존 모든 필드 포함
            "percentile_rank": percentile_rank,
            "score_differences": score_differences
        }
        
        logger.info(f"✅ 직원 검색 성공: {target_employee['uid']}")
        
        return EmployeeSearchResponse(
            employee=response_employee_data,
            statistics={
                "total_count": total_count,
                "average_scores": avg_scores,
                "dimension_averages": _extract_dimension_averages(all_results),
                "grade_distribution": grade_counts,
                "top_grade_ratio": top_grade_ratio
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 직원 검색 오류: {e}")
        import traceback
        logger.error(f"상세 오류: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="검색 중 오류가 발생했습니다")


@router.get("/employees/{job_id}", response_model=EmployeeListResponse)
async def get_employees_list(
    job_id: str,
    limit: int = Query(50, description="최대 결과 수"),
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """직원 목록 조회 (자동완성용) - SQLiteService 호환"""
    try:
        # Job 확인
        job = await sqlite_service.get_analysis_job(job_id)
        if not job or job.get('status') != 'completed':
            raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
        
        # 결과 조회
        all_results = await sqlite_service.get_analysis_results(job_id)
        
        # 점수순 정렬 후 제한
        sorted_results = sorted(
            all_results, 
            key=lambda x: x['result_data'].get('AIRISS_v2_종합점수', 0), 
            reverse=True
        )[:limit]
        
        employee_list = [
            {
                "uid": result['uid'],
                "grade": result['result_data'].get('OK등급', 'N/A'),
                "score": result['result_data'].get('AIRISS_v2_종합점수', 0)
            }
            for result in sorted_results
        ]
        
        return EmployeeListResponse(employees=employee_list)
        
    except Exception as e:
        logger.error(f"❌ 직원 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="목록 조회 실패")


def _extract_dimension_averages(all_results):
    """8대 영역별 평균 계산 - SQLiteService 데이터 구조용"""
    dimensions = [
        "업무성과", "리더십협업", "커뮤니케이션", "전문성학습",
        "태도열정", "혁신창의", "고객지향", "윤리준수"
    ]
    
    dimension_sums = {dim: [] for dim in dimensions}
    
    for result in all_results:
        result_data = result['result_data']
        for dim in dimensions:
            # 텍스트 점수 키 찾기
            score_key = f"{dim}_텍스트점수"
            score = result_data.get(score_key, 0)
            if score > 0:  # 유효한 점수만 포함
                dimension_sums[dim].append(score)
    
    # 평균 계산
    dimension_averages = {}
    for dim in dimensions:
        scores = dimension_sums[dim]
        if scores:
            dimension_averages[dim] = round(sum(scores) / len(scores), 1)
        else:
            dimension_averages[dim] = 50.0  # 기본값
    
    return dimension_averages


# 추가 유틸리티 엔드포인트들

@router.get("/employees/{job_id}/uids")
async def get_uid_list(
    job_id: str, 
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """해당 job_id의 모든 UID 목록 반환 (드롭다운용)"""
    job = await sqlite_service.get_analysis_job(job_id)
    if not job or job.get('status') != 'completed':
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    all_results = await sqlite_service.get_analysis_results(job_id)
    uids = [result['uid'] for result in all_results]
    return {"uids": uids}


@router.get("/employees/{job_id}/grades")
async def get_grade_list(
    job_id: str, 
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """해당 job_id의 모든 OK등급 목록 반환 (드롭다운용)"""
    job = await sqlite_service.get_analysis_job(job_id)
    if not job or job.get('status') != 'completed':
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    all_results = await sqlite_service.get_analysis_results(job_id)
    grades = list(set(result['result_data'].get('OK등급', 'N/A') for result in all_results))
    return {"grades": grades}


@router.get("/employee/{job_id}/{uid}")
async def get_employee_detail(
    job_id: str, 
    uid: str, 
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """해당 job_id, uid의 직원 상세 정보 반환"""
    job = await sqlite_service.get_analysis_job(job_id)
    if not job or job.get('status') != 'completed':
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    all_results = await sqlite_service.get_analysis_results(job_id)
    employee = next((r for r in all_results if r['uid'].strip().lower() == uid.strip().lower()), None)
    
    if not employee:
        raise HTTPException(status_code=404, detail="해당 UID의 직원 결과가 없습니다")
    
    return {"employee": employee['result_data']}


@router.get("/grade/{job_id}/{grade}")
async def get_employees_by_grade(
    job_id: str, 
    grade: str, 
    sqlite_service: SQLiteService = Depends(get_sqlite_service)
):
    """해당 job_id, grade의 모든 직원 목록 반환"""
    job = await sqlite_service.get_analysis_job(job_id)
    if not job or job.get('status') != 'completed':
        raise HTTPException(status_code=404, detail="완료된 작업을 찾을 수 없습니다")
    
    all_results = await sqlite_service.get_analysis_results(job_id)
    employees = [
        r['result_data'] for r in all_results 
        if r['result_data'].get('OK등급', '').replace(' ', '').lower() == grade.replace(' ', '').lower()
    ]
    
    return {"employees": employees}
