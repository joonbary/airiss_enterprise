"""직원 관련 스키마"""

from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class EmployeeData(BaseModel):
    """직원 데이터"""
    UID: str
    원본의견: str
    AIRISS_v2_종합점수: float
    OK등급: str
    등급설명: str
    백분위: str
    분석신뢰도: float
    텍스트_종합점수: float
    정량_종합점수: float
    정량_데이터품질: str
    AI_장점: str
    AI_개선점: str
    AI_종합피드백: str
    percentile_rank: Optional[float] = None
    score_differences: Optional[Dict[str, float]] = None
    
    class Config:
        extra = "allow"  # 8대 영역 점수 등 추가 필드 허용


class EmployeeStatistics(BaseModel):
    """전체 통계 정보"""
    total_count: int
    average_scores: Dict[str, float]
    dimension_averages: Dict[str, float]
    grade_distribution: Dict[str, int]
    top_grade_ratio: float


class EmployeeSearchResponse(BaseModel):
    """직원 검색 응답"""
    employee: EmployeeData
    statistics: EmployeeStatistics


class EmployeeListItem(BaseModel):
    """직원 목록 아이템"""
    uid: str
    grade: str
    score: float


class EmployeeListResponse(BaseModel):
    """직원 목록 응답"""
    employees: List[EmployeeListItem]