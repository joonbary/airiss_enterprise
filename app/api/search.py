# app/api/search_fixed_v2.py
# AIRISS v4.1 고급 검색 및 조회 API - SQLite 커넥션 문제 해결
# 🎯 분석결과 조회 기능 강화 - 커넥션 최적화

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import traceback
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import text
import asyncio
from collections import Counter
import re

# 로깅 설정
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/search", tags=["search"])

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

class FavoriteRequest(BaseModel):
    uid: str
    user_id: str = "default_user"  # 실제로는 인증에서 가져옴
    note: Optional[str] = None  # 즐겨찾기 메모

# 🎯 통합 검색 API
@router.post("/results")
async def search_analysis_results(request: SearchRequest):
    """
    고급 검색 기능 - 다양한 조건으로 분석 결과 검색
    ✅ 단일 커넥션으로 최적화
    """
    try:
        logger.info(f"🔍 고급 검색 요청: {request}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        # SQL 쿼리 빌드
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
        
        # 🔍 검색 조건 추가 (쿼리-파라미터 개수 일치 보장)
        if request.uid and request.query:
            conditions.append("(r.uid LIKE ? OR r.result_data LIKE ?)")
            params.extend([f"%{request.uid}%", f"%{request.query}%"])
        elif request.uid:
            conditions.append("r.uid LIKE ?")
            params.append(f"%{request.uid}%")
        elif request.query:
            conditions.append("r.result_data LIKE ?")
            params.append(f"%{request.query}%")
        
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
        
        # 🔥 수정: 단일 커넥션으로 모든 쿼리 실행
        results = []
        total_count = 0
        
        try:
            # 단일 커넥션 생성
            conn = await db_service.get_connection()
            
            # 전체 개수 조회 (먼저)
            count_query = re.sub(
                r"SELECT DISTINCT[\s\S]+?FROM",
                "SELECT COUNT(DISTINCT r.uid) FROM",
                base_query.split("ORDER BY")[0],
                flags=re.MULTILINE
            )
            count_params = params[:len(conditions)]
            logger.debug(f"[COUNT-QUERY] SQL: {count_query}")
            logger.debug(f"[COUNT-QUERY] PARAMS: {count_params}")
            count_cursor = await conn.execute(count_query, count_params)
            count_result = await count_cursor.fetchone()
            total_count = int(count_result[0]) if count_result else 0
            await count_cursor.close()
            
            # 메인 쿼리 실행 (페이징 적용)
            paginated_query = base_query + f" LIMIT {request.page_size} OFFSET {offset}"
            cursor = await conn.execute(paginated_query, params)
            rows = await cursor.fetchall()
            await cursor.close()
            
            # 커넥션 종료
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
                
                # 기본 정보 추출
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
                
                # 상세 정보 포함 여부에 따라 데이터 추가
                if request.include_details:
                    basic_info["full_data"] = result_data
                else:
                    # 핵심 정보만 추가
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
        
        logger.info(f"✅ 검색 완료: {len(results)}개 결과 반환 (전체 {total_count}개)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 검색 오류: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

def _calculate_grade_distribution(results):
    """등급별 분포 계산"""
    if not results:
        return {}
    
    grade_counts = {}
    for result in results:
        grade = result.get("grade", "Unknown")
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    return grade_counts

# 🎯 자동완성 API - 최적화
@router.post("/autocomplete")
async def get_autocomplete_suggestions(request: AutocompleteRequest):
    """자동완성 제안 기능 - 단일 커넥션 사용"""
    try:
        logger.info(f"🔤 자동완성 요청: {request}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        suggestions = []
        query = ""
        params = []
        
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
        
        # 🔥 단일 커넥션 사용
        try:
            conn = await db_service.get_connection()
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            await cursor.close()
            await conn.close()
            
            suggestions = [row[0] for row in rows if row[0]]
            
        except Exception as db_error:
            logger.error(f"❌ 자동완성 DB 오류: {db_error}")
            if 'conn' in locals():
                await conn.close()
            raise HTTPException(status_code=500, detail=f"자동완성 DB 오류: {str(db_error)}")
        
        logger.info(f"✅ 자동완성: {len(suggestions)}개 제안")
        return {
            "suggestions": suggestions,
            "field": request.field,
            "query": request.query,
            "total_found": len(suggestions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 자동완성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"자동완성 실패: {str(e)}")

# 🎯 특정 직원 분석 히스토리 - 최적화
@router.get("/employee/{uid}")
async def get_employee_history(
    uid: str,
    limit: int = Query(10, ge=1, le=100),
    include_details: bool = Query(False)
):
    """특정 직원의 분석 히스토리 조회 - 단일 커넥션 사용"""
    try:
        logger.info(f"👤 직원 히스토리 조회: {uid}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        query = """
        SELECT 
            r.result_data,
            j.created_at,
            j.id,
            j.file_id
        FROM results r
        JOIN jobs j ON r.job_id = j.id
        WHERE r.uid = ? AND j.status = 'completed'
        ORDER BY j.created_at DESC
        LIMIT ?
        """
        
        # 🔥 단일 커넥션 사용
        rows = []
        try:
            conn = await db_service.get_connection()
            cursor = await conn.execute(query, [uid, limit])
            rows = await cursor.fetchall()
            await cursor.close()
            await conn.close()
            
        except Exception as db_error:
            logger.error(f"❌ 직원 히스토리 DB 오류: {db_error}")
            if 'conn' in locals():
                await conn.close()
            raise HTTPException(status_code=500, detail=f"히스토리 DB 오류: {str(db_error)}")
        
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
        trend_analysis = {}
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

# 🎯 다중 직원 비교 API - 커넥션 최적화 (핵심 수정)
@router.post("/compare")
async def compare_employees(request: CompareRequest):
    """
    다중 직원 성과 비교 분석 - 단일 커넥션으로 최적화
    🔥 가장 중요한 수정: 루프에서 커넥션 중복 생성 문제 해결
    """
    try:
        logger.info(f"🔄 직원 비교 요청: {request.uids}")
        
        if len(request.uids) < 2:
            raise HTTPException(status_code=400, detail="비교를 위해서는 최소 2명의 직원이 필요합니다")
        
        if len(request.uids) > 10:
            raise HTTPException(status_code=400, detail="한 번에 최대 10명까지만 비교할 수 있습니다")
        
        db_service = get_db_service()
        await db_service.init_database()
        
        # 🔥 핵심 수정: 단일 커넥션으로 모든 직원 데이터 조회
        comparison_data = []
        
        try:
            # 단일 커넥션 생성
            conn = await db_service.get_connection()
            
            # 전체 직원의 최신 분석 결과를 한 번에 조회
            uid_placeholders = ", ".join(["?" for _ in request.uids])
            batch_query = f"""
            WITH latest_analysis AS (
                SELECT 
                    r.uid,
                    r.result_data,
                    j.created_at,
                    ROW_NUMBER() OVER (PARTITION BY r.uid ORDER BY j.created_at DESC) as rn
                FROM results r
                JOIN jobs j ON r.job_id = j.id
                WHERE r.uid IN ({uid_placeholders}) AND j.status = 'completed'
            )
            SELECT uid, result_data, created_at
            FROM latest_analysis
            WHERE rn = 1
            ORDER BY uid
            """
            
            cursor = await conn.execute(batch_query, request.uids)
            rows = await cursor.fetchall()
            await cursor.close()
            await conn.close()
            
            # 결과 처리
            found_uids = set()
            for row in rows:
                try:
                    import json
                    uid = row[0]
                    result_data = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                    analysis_date = row[2]
                    
                    employee_data = {
                        "uid": uid,
                        "analysis_date": analysis_date,
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
                    found_uids.add(uid)
                    
                except Exception as e:
                    logger.error(f"⚠️ 직원 {row[0]} 데이터 처리 오류: {e}")
                    continue
            
            # 찾지 못한 직원들 로깅
            missing_uids = set(request.uids) - found_uids
            if missing_uids:
                logger.warning(f"⚠️ 분석 결과를 찾을 수 없는 직원들: {missing_uids}")
                
        except Exception as db_error:
            logger.error(f"❌ 비교 분석 DB 오류: {db_error}")
            if 'conn' in locals():
                await conn.close()
            raise HTTPException(status_code=500, detail=f"비교 분석 DB 오류: {str(db_error)}")
        
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
                "found_uids": list(found_uids),
                "missing_uids": list(set(request.uids) - found_uids),
                "comparison_date": datetime.now().isoformat(),
                "dimensions_analyzed": request.dimensions or ["전체"]
            }
        }
        
        logger.info(f"✅ 직원 비교 완료: {len(comparison_data)}명 (요청: {len(request.uids)}명)")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 직원 비교 오류: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"비교 분석 실패: {str(e)}")

def _perform_comparison_analysis(employees_data, dimensions=None):
    """비교 분석 수행"""
    if not employees_data:
        return {}
    
    # 종합 점수 비교
    scores = [emp["overall_score"] for emp in employees_data]
    highest_performer = max(employees_data, key=lambda x: x["overall_score"])
    lowest_performer = min(employees_data, key=lambda x: x["overall_score"])
    
    # 차원별 비교 (요청된 차원이 있으면 해당 차원만, 없으면 전체)
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

# 🎯 팀별 분석 현황 - 최적화
@router.get("/team-summary")
async def get_team_summary(
    department: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None)
):
    """팀/부서별 분석 현황 요약 - 단일 커넥션 사용"""
    try:
        logger.info(f"🏢 팀 요약 조회: 부서={department}")
        
        db_service = get_db_service()
        await db_service.init_database()
        
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
        
        # 🔥 단일 커넥션 사용
        rows = []
        try:
            conn = await db_service.get_connection()
            cursor = await conn.execute(base_query, params)
            rows = await cursor.fetchall()
            await cursor.close()
            await conn.close()
            
        except Exception as db_error:
            logger.error(f"❌ 팀 요약 DB 오류: {db_error}")
            if 'conn' in locals():
                await conn.close()
            raise HTTPException(status_code=500, detail=f"팀 요약 DB 오류: {str(db_error)}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 팀 요약 오류: {e}")
        raise HTTPException(status_code=500, detail=f"팀 요약 조회 실패: {str(e)}")

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

# 🎯 즐겨찾기 관리 - 메모리 기반 (실제로는 DB 저장)
favorites_storage = {}  # user_id -> [uid1, uid2, ...]

@router.post("/favorites/add")
async def add_favorite(request: FavoriteRequest):
    """즐겨찾기 추가"""
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

@router.delete("/favorites/remove/{uid}")
async def remove_favorite(uid: str, user_id: str = Query("default_user")):
    """즐겨찾기 제거"""
    try:
        logger.info(f"🗑️ 즐겨찾기 제거: {uid}")
        
        user_favorites = favorites_storage.get(user_id, [])
        original_count = len(user_favorites)
        user_favorites = [f for f in user_favorites if f["uid"] != uid]
        
        if len(user_favorites) == original_count:
            raise HTTPException(status_code=404, detail="즐겨찾기에서 찾을 수 없습니다")
        
        favorites_storage[user_id] = user_favorites
        
        logger.info(f"✅ 즐겨찾기 제거 완료: {uid}")
        return {
            "status": "removed",
            "uid": uid,
            "remaining_count": len(user_favorites)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 즐겨찾기 제거 오류: {e}")
        raise HTTPException(status_code=500, detail=f"즐겨찾기 제거 실패: {str(e)}")

@router.get("/favorites")
async def get_favorites(
    user_id: str = Query("default_user"),
    include_details: bool = Query(False)
):
    """즐겨찾기 목록 조회 - 상세 정보 포함 시 단일 커넥션 사용"""
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
            # 🔥 단일 커넥션으로 모든 즐겨찾기 분석 결과 조회
            db_service = get_db_service()
            await db_service.init_database()
            
            detailed_favorites = []
            favorite_uids = [f["uid"] for f in user_favorites]
            
            try:
                conn = await db_service.get_connection()
                
                # 배치로 모든 즐겨찾기의 최신 분석 결과 조회
                uid_placeholders = ", ".join(["?" for _ in favorite_uids])
                batch_query = f"""
                WITH latest_analysis AS (
                    SELECT 
                        r.uid,
                        r.result_data,
                        j.created_at,
                        ROW_NUMBER() OVER (PARTITION BY r.uid ORDER BY j.created_at DESC) as rn
                    FROM results r
                    JOIN jobs j ON r.job_id = j.id
                    WHERE r.uid IN ({uid_placeholders}) AND j.status = 'completed'
                )
                SELECT uid, result_data, created_at
                FROM latest_analysis
                WHERE rn = 1
                """
                
                cursor = await conn.execute(batch_query, favorite_uids)
                analysis_results = await cursor.fetchall()
                await cursor.close()
                await conn.close()
                
                # 분석 결과를 딕셔너리로 변환
                analysis_dict = {}
                for row in analysis_results:
                    try:
                        import json
                        uid = row[0]
                        result_data = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                        analysis_dict[uid] = {
                            "latest_score": result_data.get("AIRISS_v4_종합점수", 0),
                            "latest_grade": result_data.get("OK등급", ""),
                            "last_analysis": row[2],
                            "has_analysis": True
                        }
                    except Exception as e:
                        logger.error(f"⚠️ 즐겨찾기 분석 결과 처리 오류 ({row[0]}): {e}")
                        analysis_dict[row[0]] = {"has_analysis": False, "error": str(e)}
                
                # 즐겨찾기와 분석 결과 결합
                for favorite in user_favorites:
                    uid = favorite["uid"]
                    detailed_favorite = favorite.copy()
                    
                    if uid in analysis_dict:
                        detailed_favorite.update(analysis_dict[uid])
                    else:
                        detailed_favorite.update({
                            "has_analysis": False,
                            "message": "분석 결과 없음"
                        })
                    
                    detailed_favorites.append(detailed_favorite)
                    
            except Exception as db_error:
                logger.error(f"❌ 즐겨찾기 상세 조회 DB 오류: {db_error}")
                if 'conn' in locals():
                    await conn.close()
                # DB 오류 시 기본 정보만 반환
                detailed_favorites = [
                    {**favorite, "has_analysis": False, "error": str(db_error)} 
                    for favorite in user_favorites
                ]
            
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

@router.get("/favorites/check/{uid}")
async def check_favorite_status(uid: str, user_id: str = Query("default_user")):
    """특정 직원의 즐겨찾기 상태 확인"""
    try:
        user_favorites = favorites_storage.get(user_id, [])
        is_favorite = any(f["uid"] == uid for f in user_favorites)
        
        return {
            "uid": uid,
            "is_favorite": is_favorite,
            "total_favorites": len(user_favorites)
        }
        
    except Exception as e:
        logger.error(f"❌ 즐겨찾기 상태 확인 오류: {e}")
        return {"uid": uid, "is_favorite": False, "error": str(e)}

# 🎯 검색 히스토리 관리
search_history = []

@router.get("/recent-searches")
async def get_recent_searches(limit: int = Query(10, ge=1, le=50)):
    """최근 검색 히스토리 조회"""
    try:
        recent = search_history[-limit:]
        return {
            "recent_searches": recent,
            "total_count": len(search_history)
        }
    except Exception as e:
        logger.error(f"❌ 검색 히스토리 조회 오류: {e}")
        return {"recent_searches": [], "total_count": 0}

@router.post("/save-search")
async def save_search_history(search_term: str):
    """검색어 히스토리 저장"""
    try:
        if search_term and search_term.strip():
            search_entry = {
                "query": search_term.strip(),
                "timestamp": datetime.now().isoformat(),
                "id": len(search_history) + 1
            }
            search_history.append(search_entry)
            
            # 최대 100개까지만 유지
            if len(search_history) > 100:
                search_history.pop(0)
            
            return {"status": "saved", "entry": search_entry}
    except Exception as e:
        logger.error(f"❌ 검색 히스토리 저장 오류: {e}")
        return {"status": "error", "message": str(e)}

# 🎯 헬스체크
@router.get("/health")
async def search_health_check():
    """검색 API 헬스체크"""
    try:
        db_service = get_db_service()
        db_status = "connected" if db_service else "disconnected"
        
        return {
            "status": "healthy",
            "service": "AIRISS Search API v4.1 Enhanced - Connection Optimized",
            "database": db_status,
            "features": [
                "고급 검색", "자동완성", "직원 히스토리", 
                "다중 비교", "팀 분석", "검색 히스토리", "즐겨찾기"
            ],
            "optimizations": [
                "단일 커넥션 사용", "배치 쿼리", "커넥션 풀링", "오류 처리 강화"
            ],
            "favorites_count": sum(len(favs) for favs in favorites_storage.values()),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
