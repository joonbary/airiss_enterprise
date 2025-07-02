# app/api/search_fixed.py - SQLite Connection 오류 완전 해결 버전
# 🎯 "threads can only be started once" 오류 완전 해결
# AIRISS v4.1 고급 검색 및 조회 API
# 🎯 실제 DB 스키마 사용: files, jobs, results

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import traceback
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import text
from collections import Counter

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/search-fixed", tags=["search-fixed"])

def get_db_service():
    """DB 서비스 가져오기 - 항상 새 인스턴스 반환"""
    from app.db.sqlite_service import SQLiteService
    return SQLiteService()

# 🆕 검색 요청 모델
class SearchRequest(BaseModel):
    query: Optional[str] = None  # 통합 검색어
    uid: Optional[str] = None    # 특정 직원 ID
    department: Optional[str] = None  # 부서
    grade: Optional[str] = None  # 등급 (OK★★★, OK★★, etc.)
    score_min: Optional[float] = None  # 최소 점수
    score_max: Optional[float] = None  # 최대 점수
    date_from: Optional[str] = None   # 분석 시작 날짜
    date_to: Optional[str] = None     # 분석 종료 날짜
    sort_by: str = "score"  # 정렬 기준: score, date, name, grade
    sort_order: str = "desc"  # 정렬 순서: asc, desc
    page: int = 1           # 페이지 번호
    page_size: int = 20     # 페이지 크기
    include_details: bool = False  # 상세 정보 포함 여부

class AutocompleteRequest(BaseModel):
    query: str
    field: str = "uid"  # uid, department, name
    limit: int = 10

class CompareRequest(BaseModel):
    uids: List[str]  # 비교할 직원 ID 목록
    dimensions: Optional[List[str]] = None  # 비교할 차원

# 🔥 핵심 해결: 커넥션 재사용 함수 추가
async def execute_with_single_connection(db_service, queries_and_params):
    """
    단일 커넥션으로 여러 쿼리를 안전하게 실행
    
    Args:
        db_service: SQLite 서비스 인스턴스
        queries_and_params: [(query1, params1), (query2, params2), ...] 형태의 리스트
    
    Returns:
        [result1, result2, ...] 형태의 결과 리스트
    """
    results = []
    
    # 🔥 핵심: 하나의 커넥션으로 모든 쿼리 실행
    async with aiosqlite.connect(db_service.db_path) as conn:
        for query, params in queries_and_params:
            cursor = await conn.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                if "COUNT(" in query.upper():
                    # COUNT 쿼리는 단일 값 반환
                    result = await cursor.fetchone()
                    results.append(result[0] if result else 0)
                else:
                    # 일반 SELECT 쿼리는 모든 행 반환
                    result = await cursor.fetchall()
                    results.append(result)
            else:
                # INSERT, UPDATE, DELETE 등
                await conn.commit()
                results.append(cursor.rowcount)
    
    return results

# 🎯 통합 검색 API - 올바른 테이블명 사용
@router.post("/results")
async def search_analysis_results(request: SearchRequest):
    """
    고급 검색 기능 - 올바른 테이블명 사용
    ✅ 실제 DB 스키마: files, jobs, results
    """
    try:
        logger.info(f"🔍 검색 요청 (올바른 테이블): {request}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        # ✅ 올바른 테이블명 사용: results, jobs
        base_query = """
        SELECT DISTINCT
            r.uid,
            r.result_data,
            j.created_at as analysis_date,
            j.file_id,
            j.id as job_id
        FROM results r
        JOIN jobs j ON r.job_id = j.id
        WHERE j.status = 'completed'
        """
        
        params = []
        conditions = []
        
        # 검색 조건 추가
        if request.uid:
            conditions.append("r.uid LIKE ?")
            params.append(f"%{request.uid}%")
        
        if request.query:
            conditions.append("(r.uid LIKE ? OR r.result_data LIKE ?)")
            params.extend([f"%{request.query}%", f"%{request.query}%"])
        
        if request.department:
            conditions.append("r.result_data LIKE ?")
            params.append(f'%"부서":"%{request.department}%"%')
        
        if request.grade:
            conditions.append("r.result_data LIKE ?")
            params.append(f'%"OK등급":"{request.grade}"%')
        
        # 점수 범위 필터링
        if request.score_min is not None:
            conditions.append("CAST(json_extract(r.result_data, '$.AIRISS_v4_종합점수') AS REAL) >= ?")
            params.append(request.score_min)
        
        if request.score_max is not None:
            conditions.append("CAST(json_extract(r.result_data, '$.AIRISS_v4_종합점수') AS REAL) <= ?")
            params.append(request.score_max)
        
        # 날짜 범위 필터링
        if request.date_from:
            conditions.append("j.created_at >= ?")
            params.append(request.date_from)
        
        if request.date_to:
            conditions.append("j.created_at <= ?")
            params.append(request.date_to)
        
        # WHERE 절 추가
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # 정렬 추가
        order_mapping = {
            "score": "CAST(json_extract(r.result_data, '$.AIRISS_v4_종합점수') AS REAL)",
            "date": "j.created_at",
            "name": "r.uid",
            "grade": "json_extract(r.result_data, '$.OK등급')"
        }
        
        order_column = order_mapping.get(request.sort_by, order_mapping["score"])
        order_direction = "DESC" if request.sort_order.lower() == "desc" else "ASC"
        base_query += f" ORDER BY {order_column} {order_direction}"
        
        # 페이징 추가
        offset = (request.page - 1) * request.page_size
        
        # 단일 커넥션으로 쿼리 실행
        results = []
        total_count = 0
        
        try:
            conn = await db_service.get_connection()
            
            # 전체 개수 조회
            count_query = base_query.split("ORDER BY")[0].replace(
                "SELECT DISTINCT r.uid, r.result_data, j.created_at as analysis_date, j.file_id, j.id as job_id",
                "SELECT COUNT(DISTINCT r.uid)"
            )
            
            count_cursor = await conn.execute(count_query, params)
            count_result = await count_cursor.fetchone()
            total_count = count_result[0] if count_result else 0
            await count_cursor.close()
            
            # 메인 쿼리 실행 (페이징 적용)
            paginated_query = base_query + f" LIMIT {request.page_size} OFFSET {offset}"
            cursor = await conn.execute(paginated_query, params)
            rows = await cursor.fetchall()
            await cursor.close()
            
            await conn.close()
            
        except Exception as db_error:
            logger.error(f"❌ DB 쿼리 오류: {db_error}")
            if 'conn' in locals():
                await conn.close()
            raise HTTPException(status_code=500, detail=f"데이터베이스 오류: {str(db_error)}")
        
        # 결과 처리
        for row in rows:
            try:
                import json
                result_data = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                
                basic_info = {
                    "uid": row[0],
                    "analysis_date": row[2],
                    "file_id": row[3],
                    "job_id": row[4],
                    "score": result_data.get("AIRISS_v4_종합점수", 0),
                    "grade": result_data.get("OK등급", ""),
                    "grade_description": result_data.get("등급설명", ""),
                    "percentile": result_data.get("백분위", ""),
                    "confidence": result_data.get("분석신뢰도", 0)
                }
                
                if request.include_details:
                    basic_info["full_data"] = result_data
                else:
                    basic_info.update({
                        "dimension_scores": {
                            "업무성과": result_data.get("업무성과_점수", 0),
                            "KPI달성": result_data.get("KPI달성_점수", 0),
                            "태도마인드": result_data.get("태도마인드_점수", 0),
                            "커뮤니케이션": result_data.get("커뮤니케이션_점수", 0),
                            "리더십협업": result_data.get("리더십협업_점수", 0),
                            "전문성학습": result_data.get("전문성학습_점수", 0),
                            "창의혁신": result_data.get("창의혁신_점수", 0),
                            "조직적응": result_data.get("조직적응_점수", 0)
                        },
                        "analysis_mode": result_data.get("분석모드", ""),
                        "analysis_system": result_data.get("분석시스템", "")
                    })
                
                results.append(basic_info)
                
            except Exception as e:
                logger.error(f"⚠️ 결과 처리 오류: {e}")
                continue
        
        # 응답 구성
        response = {
            "results": results,
            "pagination": {
                "page": request.page,
                "page_size": request.page_size,
                "total_count": total_count,
                "total_pages": (total_count + request.page_size - 1) // request.page_size if total_count > 0 else 0
            },
            "search_info": {
                "query": request.query,
                "filters_applied": len(conditions),
                "sort_by": request.sort_by,
                "sort_order": request.sort_order
            },
            "summary": {
                "found_count": len(results),
                "avg_score": round(np.mean([r["score"] for r in results]), 1) if results else 0,
                "grade_distribution": _calculate_grade_distribution(results)
            }
        }
        
        logger.info(f"✅ 검색 완료 (올바른 테이블): {len(results)}개 결과 반환")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 검색 오류: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

# 🎯 자동완성 API - 커넥션 오류 해결
@router.post("/autocomplete")
async def get_autocomplete_suggestions(request: AutocompleteRequest):
    """자동완성 제안 기능 - 커넥션 안전 버전"""
    try:
        logger.info(f"🔤 자동완성 요청: {request}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        import aiosqlite
        
        suggestions = []
        
        if request.field == "uid":
            query = """
            SELECT DISTINCT r.uid
            FROM results r
            WHERE r.uid LIKE ?
            ORDER BY r.uid
            LIMIT ?
            """
            params = [f"%{request.query}%", request.limit]
            
        elif request.field == "grade":
            query = """
            SELECT DISTINCT json_extract(r.result_data, '$.OK등급') as grade
            FROM results r
            WHERE json_extract(r.result_data, '$.OK등급') LIKE ?
            ORDER BY grade
            LIMIT ?
            """
            params = [f"%{request.query}%", request.limit]
            
        elif request.field == "department":
            query = """
            SELECT DISTINCT json_extract(r.result_data, '$.부서') as dept
            FROM results r
            WHERE json_extract(r.result_data, '$.부서') LIKE ?
            AND json_extract(r.result_data, '$.부서') IS NOT NULL
            ORDER BY dept
            LIMIT ?
            """
            params = [f"%{request.query}%", request.limit]
            
        else:
            return {"suggestions": [], "message": "지원하지 않는 필드입니다"}
        
        # 🔥 해결: 단일 커넥션으로 실행
        results = await execute_with_single_connection(db_service, [(query, params)])
        rows = results[0]
        
        suggestions = [row[0] for row in rows if row[0]]
        
        logger.info(f"✅ 자동완성: {len(suggestions)}개 제안")
        return {
            "suggestions": suggestions,
            "field": request.field,
            "query": request.query,
            "total_found": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"❌ 자동완성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동완성 실패: {str(e)}")

# 🎯 특정 직원 분석 히스토리 - 커넥션 오류 해결
@router.get("/employee/{uid}")
async def get_employee_history(
    uid: str,
    limit: int = Query(10, ge=1, le=100),
    include_details: bool = Query(False)
):
    """특정 직원의 분석 히스토리 조회 - 커넥션 안전 버전"""
    try:
        logger.info(f"👤 직원 히스토리 조회: {uid}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        import aiosqlite
        
        query = """
        SELECT 
            r.result_data,
            j.created_at,
            j.id as job_id,
            j.file_id
        FROM results r
        JOIN jobs j ON r.job_id = j.id
        WHERE r.uid = ? AND j.status = 'completed'
        ORDER BY j.created_at DESC
        LIMIT ?
        """
        
        # 🔥 해결: 단일 쿼리로 실행
        results = await execute_with_single_connection(db_service, [(query, [uid, limit])])
        rows = results[0]
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"직원 {uid}의 분석 기록을 찾을 수 없습니다")
        
        history = []
        scores = []
        grades = []
        dates = []
        
        for row in rows:
            try:
                import json
                result_data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                
                analysis_date = row[1]
                score = result_data.get("AIRISS_v4_종합점수", 0)
                grade = result_data.get("OK등급", "")
                
                entry = {
                    "analysis_date": analysis_date,
                    "job_id": row[2],
                    "file_id": row[3],
                    "score": score,
                    "grade": grade,
                    "confidence": result_data.get("분석신뢰도", 0)
                }
                
                if include_details:
                    entry["full_data"] = result_data
                else:
                    entry["summary"] = {
                        "top_strength": result_data.get("주요강점_1영역", ""),
                        "improvement_area": result_data.get("개선필요_1영역", ""),
                        "ai_suggestion": result_data.get("AI개선제안_1", "")
                    }
                
                history.append(entry)
                scores.append(score)
                grades.append(grade)
                dates.append(analysis_date)
                
            except Exception as e:
                logger.error(f"⚠️ 히스토리 항목 처리 오류: {e}")
                continue
        
        # 통계 계산
        if scores:
            latest_score = scores[0]
            previous_score = scores[1] if len(scores) > 1 else scores[0]
            score_change = latest_score - previous_score
            
            trend_analysis = {
                "latest_score": latest_score,
                "previous_score": previous_score,
                "score_change": round(score_change, 1),
                "trend": "상승" if score_change > 0 else "하락" if score_change < 0 else "유지",
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "average_score": round(np.mean(scores), 1),
                "analysis_count": len(scores)
            }
        else:
            trend_analysis = {}
        
        response = {
            "uid": uid,
            "history": history,
            "trend_analysis": trend_analysis,
            "grade_changes": _analyze_grade_changes(grades, dates),
            "total_analyses": len(history)
        }
        
        logger.info(f"✅ 직원 히스토리: {len(history)}개 분석 기록")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 직원 히스토리 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"히스토리 조회 실패: {str(e)}")

# 🎯 다중 직원 비교 API - 완전히 재작성 (핵심 수정)
@router.post("/compare")
async def compare_employees(request: CompareRequest):
    """
    다중 직원 성과 비교 분석 - 커넥션 오류 완전 해결
    """
    try:
        logger.info(f"🔄 직원 비교 요청: {request.uids}")
        
        if len(request.uids) < 2:
            raise HTTPException(status_code=400, detail="비교를 위해서는 최소 2명의 직원이 필요합니다")
        
        if len(request.uids) > 10:
            raise HTTPException(status_code=400, detail="한 번에 최대 10명까지만 비교할 수 있습니다")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        import aiosqlite
        
        # 🔥 핵심 해결: 모든 직원을 한 번의 쿼리로 조회
        uid_placeholders = ','.join(['?' for _ in request.uids])
        batch_query = f"""
        SELECT 
            r.uid,
            r.result_data, 
            j.created_at,
            ROW_NUMBER() OVER (PARTITION BY r.uid ORDER BY j.created_at DESC) as rn
        FROM results r
        JOIN jobs j ON r.job_id = j.id
        WHERE r.uid IN ({uid_placeholders}) AND j.status = 'completed'
        ORDER BY r.uid, j.created_at DESC
        """
        
        # 🔥 단일 커넥션으로 모든 데이터 조회
        results = await execute_with_single_connection(db_service, [(batch_query, request.uids)])
        rows = results[0]
        
        # 각 직원의 최신 분석 결과만 추출
        employee_data_map = {}
        for row in rows:
            uid = row[0]
            rn = row[3]  # ROW_NUMBER
            
            # 각 직원의 첫 번째 (최신) 결과만 사용
            if rn == 1 and uid not in employee_data_map:
                employee_data_map[uid] = row
        
        # 데이터 변환
        comparison_data = []
        for uid in request.uids:
            if uid not in employee_data_map:
                logger.warning(f"⚠️ 직원 {uid}의 분석 결과를 찾을 수 없습니다")
                continue
            
            row = employee_data_map[uid]
            
            try:
                import json
                result_data = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                
                employee_data = {
                    "uid": uid,
                    "analysis_date": row[2],
                    "overall_score": result_data.get("AIRISS_v4_종합점수", 0),
                    "grade": result_data.get("OK등급", ""),
                    "dimension_scores": {
                        "업무성과": result_data.get("업무성과_점수", 0),
                        "KPI달성": result_data.get("KPI달성_점수", 0),
                        "태도마인드": result_data.get("태도마인드_점수", 0),
                        "커뮤니케이션": result_data.get("커뮤니케이션_점수", 0),
                        "리더십협업": result_data.get("리더십협업_점수", 0),
                        "전문성학습": result_data.get("전문성학습_점수", 0),
                        "창의혁신": result_data.get("창의혁신_점수", 0),
                        "조직적응": result_data.get("조직적응_점수", 0)
                    },
                    "strengths": [
                        result_data.get("주요강점_1영역", ""),
                        result_data.get("주요강점_2영역", ""),
                        result_data.get("주요강점_3영역", "")
                    ],
                    "improvements": [
                        result_data.get("개선필요_1영역", ""),
                        result_data.get("개선필요_2영역", ""),
                        result_data.get("개선필요_3영역", "")
                    ]
                }
                
                comparison_data.append(employee_data)
                
            except Exception as e:
                logger.error(f"⚠️ 직원 {uid} 데이터 처리 오류: {e}")
                continue
        
        if len(comparison_data) < 2:
            raise HTTPException(status_code=404, detail="비교할 수 있는 유효한 분석 결과가 부족합니다")
        
        # 비교 분석 수행
        comparison_analysis = _perform_comparison_analysis(comparison_data, request.dimensions)
        
        response = {
            "employees": comparison_data,
            "comparison_analysis": comparison_analysis,
            "metadata": {
                "compared_count": len(comparison_data),
                "requested_uids": request.uids,
                "comparison_date": datetime.now().isoformat(),
                "dimensions_analyzed": request.dimensions or ["전체"]
            }
        }
        
        logger.info(f"✅ 직원 비교 완료: {len(comparison_data)}명")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 직원 비교 오류: {e}")
        raise HTTPException(status_code=500, detail=f"비교 분석 실패: {str(e)}")

# 🎯 팀별 분석 현황 - 커넥션 오류 해결
@router.get("/team-summary")
async def get_team_summary(
    department: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """팀/부서별 분석 현황 요약 - 커넥션 안전 버전"""
    try:
        logger.info(f"🏢 팀 요약 조회: 부서={department}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        import aiosqlite
        
        # 기본 쿼리
        base_query = """
        SELECT 
            r.result_data,
            j.created_at
        FROM results r
        JOIN jobs j ON r.job_id = j.id
        WHERE j.status = 'completed'
        """
        
        params = []
        
        # 부서 필터
        if department:
            base_query += " AND r.result_data LIKE ?"
            params.append(f'%"부서":"%{department}%"%')
        
        # 날짜 필터
        if date_from:
            base_query += " AND j.created_at >= ?"
            params.append(date_from)
        
        if date_to:
            base_query += " AND j.created_at <= ?"
            params.append(date_to)
        
        # 🔥 해결: 단일 쿼리로 실행
        results = await execute_with_single_connection(db_service, [(base_query, params)])
        rows = results[0]
        
        # 데이터 처리
        team_data = {}
        total_analyses = 0
        
        for row in rows:
            try:
                import json
                result_data = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                
                dept = result_data.get("부서", "미분류")
                score = result_data.get("AIRISS_v4_종합점수", 0)
                grade = result_data.get("OK등급", "")
                
                if dept not in team_data:
                    team_data[dept] = {
                        "department": dept,
                        "scores": [],
                        "grades": [],
                        "analysis_count": 0
                    }
                
                team_data[dept]["scores"].append(score)
                team_data[dept]["grades"].append(grade)
                team_data[dept]["analysis_count"] += 1
                total_analyses += 1
                
            except Exception as e:
                logger.error(f"⚠️ 팀 데이터 처리 오류: {e}")
                continue
        
        # 팀별 통계 계산
        team_summary = []
        for dept, data in team_data.items():
            if data["scores"]:
                summary = {
                    "department": dept,
                    "analysis_count": data["analysis_count"],
                    "average_score": round(np.mean(data["scores"]), 1),
                    "highest_score": max(data["scores"]),
                    "lowest_score": min(data["scores"]),
                    "grade_distribution": dict(Counter(data["grades"])),
                    "performance_level": _classify_team_performance(np.mean(data["scores"]))
                }
                team_summary.append(summary)
        
        # 정렬 (평균 점수 기준)
        team_summary.sort(key=lambda x: x["average_score"], reverse=True)
        
        response = {
            "team_summary": team_summary,
            "overall_statistics": {
                "total_departments": len(team_summary),
                "total_analyses": total_analyses,
                "overall_average": round(np.mean([t["average_score"] for t in team_summary]), 1) if team_summary else 0,
                "best_performing_team": team_summary[0]["department"] if team_summary else None,
                "analysis_period": {
                    "from": date_from,
                    "to": date_to
                }
            }
        }
        
        logger.info(f"✅ 팀 요약 완료: {len(team_summary)}개 부서")
        return response
        
    except Exception as e:
        logger.error(f"❌ 팀 요약 오류: {e}")
        raise HTTPException(status_code=500, detail=f"팀 요약 조회 실패: {str(e)}")

# 🎯 즐겨찾기 관련 함수들 - 커넥션 안전 버전
class FavoriteRequest(BaseModel):
    uid: str
    user_id: str = "default_user"
    note: Optional[str] = None

# 즐겨찾기 저장소 (실제로는 DB 사용)
favorites_storage = {}

@router.post("/favorites/add")
async def add_favorite(request: FavoriteRequest):
    """즐겨찾기 추가 - 안전 버전"""
    try:
        logger.info(f"⭐ 즐겨찾기 추가: {request.uid}")
        
        user_favorites = favorites_storage.get(request.user_id, [])
        
        # 중복 체크
        existing = next((f for f in user_favorites if f["uid"] == request.uid), None)
        if existing:
            return {"status": "already_exists", "message": "이미 즐겨찾기에 있습니다"}
        
        # 즐겨찾기 추가
        favorite_entry = {
            "uid": request.uid,
            "note": request.note,
            "added_at": datetime.now().isoformat(),
            "id": len(user_favorites) + 1
        }
        
        user_favorites.append(favorite_entry)
        favorites_storage[request.user_id] = user_favorites
        
        logger.info(f"✅ 즐겨찾기 추가 완료: {request.uid}")
        return {
            "status": "added",
            "favorite": favorite_entry,
            "total_favorites": len(user_favorites)
        }
        
    except Exception as e:
        logger.error(f"❌ 즐겨찾기 추가 오류: {e}")
        raise HTTPException(status_code=500, detail=f"즐겨찾기 추가 실패: {str(e)}")

@router.get("/favorites")
async def get_favorites(
    user_id: str = Query("default_user"),
    include_details: bool = Query(False)
):
    """즐겨찾기 목록 조회 - 커넥션 안전 버전"""
    try:
        logger.info(f"⭐ 즐겨찾기 목록 조회: {user_id}")
        
        user_favorites = favorites_storage.get(user_id, [])
        
        if not user_favorites:
            return {
                "favorites": [],
                "total_count": 0,
                "message": "즐겨찾기가 없습니다"
            }
        
        # 상세 정보 포함 여부에 따라 분기
        if include_details:
            db_service = get_db_service()
            await db_service.init_database()
            
            import aiosqlite
            
            # 🔥 해결: 모든 즐겨찾기 UID를 한 번의 쿼리로 조회
            favorite_uids = [f["uid"] for f in user_favorites]
            uid_placeholders = ','.join(['?' for _ in favorite_uids])
            
            batch_query = f"""
            SELECT 
                r.uid,
                r.result_data, 
                j.created_at,
                ROW_NUMBER() OVER (PARTITION BY r.uid ORDER BY j.created_at DESC) as rn
            FROM results r
            JOIN jobs j ON r.job_id = j.id
            WHERE r.uid IN ({uid_placeholders}) AND j.status = 'completed'
            ORDER BY r.uid, j.created_at DESC
            """
            
            results = await execute_with_single_connection(db_service, [(batch_query, favorite_uids)])
            rows = results[0]
            
            # 최신 분석 결과 매핑
            latest_analysis = {}
            for row in rows:
                uid = row[0]
                rn = row[3]
                if rn == 1:  # 최신 결과만
                    latest_analysis[uid] = {
                        "result_data": row[1],
                        "created_at": row[2]
                    }
            
            # 즐겨찾기에 분석 결과 추가
            detailed_favorites = []
            for favorite in user_favorites:
                uid = favorite["uid"]
                detailed_favorite = favorite.copy()
                
                if uid in latest_analysis:
                    try:
                        import json
                        result_data = json.loads(latest_analysis[uid]["result_data"]) if isinstance(latest_analysis[uid]["result_data"], str) else latest_analysis[uid]["result_data"]
                        
                        detailed_favorite.update({
                            "latest_score": result_data.get("AIRISS_v4_종합점수", 0),
                            "latest_grade": result_data.get("OK등급", ""),
                            "last_analysis": latest_analysis[uid]["created_at"],
                            "has_analysis": True
                        })
                    except Exception as e:
                        logger.error(f"⚠️ 즐겨찾기 분석 데이터 처리 오류 ({uid}): {e}")
                        detailed_favorite.update({"has_analysis": False, "error": str(e)})
                else:
                    detailed_favorite.update({
                        "has_analysis": False,
                        "message": "분석 결과 없음"
                    })
                
                detailed_favorites.append(detailed_favorite)
            
            return {
                "favorites": detailed_favorites,
                "total_count": len(detailed_favorites),
                "include_details": True
            }
        else:
            return {
                "favorites": user_favorites,
                "total_count": len(user_favorites),
                "include_details": False
            }
        
    except Exception as e:
        logger.error(f"❌ 즐겨찾기 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"즐겨찾기 조회 실패: {str(e)}")

# 나머지 함수들 (변경 없음)
def _calculate_grade_distribution(results):
    """등급별 분포 계산"""
    if not results:
        return {}
    
    grade_counts = {}
    for result in results:
        grade = result.get("grade", "Unknown")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    return grade_counts

def _analyze_grade_changes(grades, dates):
    """등급 변화 분석"""
    if len(grades) < 2:
        return {"message": "등급 변화를 분석하기에 충분한 데이터가 없습니다"}
    
    latest_grade = grades[0]
    previous_grade = grades[1]
    
    # 등급 점수 매핑
    grade_scores = {
        "OK★★★": 100, "OK★★": 90, "OK★": 85, "OK A": 80,
        "OK B+": 75, "OK B": 70, "OK C": 60, "OK D": 40
    }
    
    latest_score = grade_scores.get(latest_grade, 50)
    previous_score = grade_scores.get(previous_grade, 50)
    
    return {
        "latest_grade": latest_grade,
        "previous_grade": previous_grade,
        "grade_change": "상승" if latest_score > previous_score else "하락" if latest_score < previous_score else "유지",
        "grade_history": grades[:5]  # 최근 5개
    }

def _perform_comparison_analysis(employees_data, dimensions=None):
    """비교 분석 수행"""
    if not employees_data:
        return {}
    
    # 종합 점수 비교
    scores = [emp["overall_score"] for emp in employees_data]
    highest_performer = max(employees_data, key=lambda x: x["overall_score"])
    lowest_performer = min(employees_data, key=lambda x: x["overall_score"])
    
    # 차원별 비교
    dimension_comparison = {}
    all_dimensions = ["업무성과", "KPI달성", "태도마인드", "커뮤니케이션", 
                     "리더십협업", "전문성학습", "창의혁신", "조직적응"]
    
    target_dimensions = dimensions if dimensions else all_dimensions
    
    for dimension in target_dimensions:
        if dimension in all_dimensions:
            dim_scores = [emp["dimension_scores"].get(dimension, 0) for emp in employees_data]
            dimension_comparison[dimension] = {
                "scores": dict(zip([emp["uid"] for emp in employees_data], dim_scores)),
                "highest": max(dim_scores),
                "lowest": min(dim_scores),
                "average": round(np.mean(dim_scores), 1),
                "range": max(dim_scores) - min(dim_scores)
            }
    
    return {
        "overall_comparison": {
            "highest_performer": {
                "uid": highest_performer["uid"],
                "score": highest_performer["overall_score"],
                "grade": highest_performer["grade"]
            },
            "lowest_performer": {
                "uid": lowest_performer["uid"],
                "score": lowest_performer["overall_score"],
                "grade": lowest_performer["grade"]
            },
            "score_range": max(scores) - min(scores),
            "average_score": round(np.mean(scores), 1)
        },
        "dimension_comparison": dimension_comparison,
        "insights": _generate_comparison_insights(employees_data)
    }

def _generate_comparison_insights(employees_data):
    """비교 인사이트 생성"""
    insights = []
    
    if len(employees_data) >= 2:
        scores = [emp["overall_score"] for emp in employees_data]
        score_range = max(scores) - min(scores)
        
        if score_range > 20:
            insights.append("직원 간 성과 편차가 큽니다. 저성과자에 대한 집중 지원이 필요할 수 있습니다.")
        elif score_range < 5:
            insights.append("직원 간 성과가 균등합니다. 팀 전체의 안정적인 성과를 보여줍니다.")
        
        # 강점 분석
        all_strengths = []
        for emp in employees_data:
            all_strengths.extend([s for s in emp["strengths"] if s])
        
        common_strengths = Counter(all_strengths).most_common(3)
        
        if common_strengths:
            insights.append(f"공통 강점 영역: {', '.join([s[0] for s in common_strengths])}")
    
    return insights

def _classify_team_performance(avg_score):
    """팀 성과 수준 분류"""
    if avg_score >= 90:
        return "최우수"
    elif avg_score >= 80:
        return "우수"
    elif avg_score >= 70:
        return "양호"
    elif avg_score >= 60:
        return "보통"
    else:
        return "개선필요"

# 기타 엔드포인트들 (간소화)
@router.delete("/favorites/remove/{uid}")
async def remove_favorite(uid: str, user_id: str = Query("default_user")):
    """즐겨찾기 제거"""
    try:
        user_favorites = favorites_storage.get(user_id, [])
        original_count = len(user_favorites)
        user_favorites = [f for f in user_favorites if f["uid"] != uid]
        
        if len(user_favorites) == original_count:
            raise HTTPException(status_code=404, detail="즐겨찾기에서 찾을 수 없습니다")
        
        favorites_storage[user_id] = user_favorites
        return {"status": "removed", "uid": uid, "remaining_count": len(user_favorites)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"즐겨찾기 제거 실패: {str(e)}")

@router.get("/health")
async def search_health_check():
    """검색 API 헬스체크 - 올바른 테이블명 사용"""
    try:
        db_service = get_db_service()
        
        # 테이블 존재 확인
        try:
            conn = await db_service.get_connection()
            
            # 테이블 목록 확인
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = await cursor.fetchall()
            table_names = [table[0] for table in tables]
            await cursor.close()
            
            # 각 테이블의 레코드 수 확인
            table_counts = {}
            for table_name in ['files', 'jobs', 'results']:
                if table_name in table_names:
                    cursor = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = (await cursor.fetchone())[0]
                    table_counts[table_name] = count
                    await cursor.close()
                else:
                    table_counts[table_name] = "존재하지 않음"
            
            await conn.close()
            
        except Exception as db_error:
            if 'conn' in locals():
                await conn.close()
            table_counts = {"error": str(db_error)}
        
        return {
            "status": "healthy",
            "service": "AIRISS Search API v4.1 - 올바른 테이블명 사용",
            "database_tables": table_counts,
            "correct_tables": ["files", "jobs", "results"],
            "api_endpoint": "/search-fixed/results",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 🎯 테이블 정보 확인
@router.get("/debug/tables")
async def debug_tables():
    """데이터베이스 테이블 정보 확인"""
    try:
        db_service = get_db_service()
        conn = await db_service.get_connection()
        
        # 모든 테이블 목록
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        await cursor.close()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            
            # 테이블 스키마
            cursor = await conn.execute(f"PRAGMA table_info({table_name})")
            schema = await cursor.fetchall()
            await cursor.close()
            
            # 레코드 수
            cursor = await conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = (await cursor.fetchone())[0]
            await cursor.close()
            
            table_info[table_name] = {
                "columns": [{"name": col[1], "type": col[2]} for col in schema],
                "record_count": count
            }
        
        await conn.close()
        
        return {
            "database_tables": table_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        if 'conn' in locals():
            await conn.close()
        return {"error": str(e)}
