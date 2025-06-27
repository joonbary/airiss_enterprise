# app/schemas/analysis.py
"""
AIRISS v4.0 분석 API 스키마
- 요청/응답 모델 정의
- Pydantic 기반 데이터 검증
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class AnalysisStartRequest(BaseModel):
    """분석 시작 요청 스키마"""
    file_id: str = Field(..., description="분석할 파일 ID")
    sample_size: int = Field(default=10, ge=1, le=1000, description="분석할 샘플 수")
    analysis_mode: str = Field(default="hybrid", description="분석 모드: text, quantitative, hybrid")
    enable_ai: bool = Field(default=False, description="AI 피드백 활성화 여부")
    ai_model: Optional[str] = Field(default="gpt-3.5-turbo", description="AI 모델명")
    ai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
    
    class Config:
        schema_extra = {
            "example": {
                "file_id": "file_12345",
                "sample_size": 25,
                "analysis_mode": "hybrid",
                "enable_ai": True,
                "ai_model": "gpt-3.5-turbo"
            }
        }

class AnalysisStartResponse(BaseModel):
    """분석 시작 응답 스키마"""
    job_id: str = Field(..., description="생성된 작업 ID")
    status: str = Field(..., description="작업 상태")
    message: str = Field(..., description="응답 메시지")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_67890",
                "status": "started",
                "message": "AIRISS v4.0 분석이 시작되었습니다"
            }
        }

class AnalysisStatusResponse(BaseModel):
    """분석 상태 조회 응답 스키마"""
    job_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="작업 상태: processing, completed, failed")
    progress: float = Field(..., ge=0, le=100, description="진행률 (0-100%)")
    total_employees: int = Field(..., description="전체 분석 대상 수")
    processed: int = Field(..., description="처리 완료 수")
    failed: int = Field(default=0, description="실패 수")
    current_employee: Optional[str] = Field(default=None, description="현재 처리 중인 직원")
    error: Optional[str] = Field(default=None, description="오류 메시지 (실패 시)")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_67890",
                "status": "processing",
                "progress": 75.5,
                "total_employees": 100,
                "processed": 75,
                "failed": 1,
                "current_employee": "EMP001",
                "error": None
            }
        }

class AnalysisResultsResponse(BaseModel):
    """분석 결과 조회 응답 스키마"""
    job_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="작업 상태")
    total_analyzed: int = Field(..., description="분석 완료된 총 수")
    failed: int = Field(default=0, description="실패 수")
    statistics: Dict[str, Any] = Field(..., description="분석 통계 정보")
    results: List[Dict[str, Any]] = Field(..., description="분석 결과 (일부)")
    data_quality: Dict[str, Any] = Field(..., description="데이터 품질 정보")
    processing_time: str = Field(..., description="처리 시간")
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "job_67890",
                "status": "completed",
                "total_analyzed": 100,
                "failed": 2,
                "statistics": {
                    "average_score": 75.2,
                    "grade_distribution": {
                        "OK★★★": 5,
                        "OK★★": 15,
                        "OK★": 25,
                        "OK A": 30,
                        "OK B": 20,
                        "OK C": 5
                    }
                },
                "results": [
                    {
                        "UID": "EMP001",
                        "AIRISS_v4_종합점수": 87.5,
                        "OK등급": "OK★★",
                        "분석신뢰도": 85.2
                    }
                ],
                "data_quality": {
                    "source": "AIRISS v4.0 DB"
                },
                "processing_time": "2분 30초"
            }
        }

class EmployeeAnalysisResult(BaseModel):
    """개별 직원 분석 결과 스키마"""
    uid: str = Field(..., description="직원 고유 ID")
    overall_score: float = Field(..., ge=0, le=100, description="종합 점수")
    grade: str = Field(..., description="OK 등급")
    percentile: float = Field(..., ge=0, le=100, description="백분위")
    text_score: float = Field(..., description="텍스트 분석 점수")
    quantitative_score: float = Field(..., description="정량 분석 점수")
    confidence: float = Field(..., description="분석 신뢰도")
    dimension_scores: Dict[str, float] = Field(..., description="8대 영역별 점수")
    ai_feedback: Optional[Dict[str, str]] = Field(default=None, description="AI 피드백")
    
    class Config:
        schema_extra = {
            "example": {
                "uid": "EMP001",
                "overall_score": 87.5,
                "grade": "OK★★",
                "percentile": 15.2,
                "text_score": 85.0,
                "quantitative_score": 90.0,
                "confidence": 88.5,
                "dimension_scores": {
                    "업무성과": 90.0,
                    "KPI달성": 85.0,
                    "태도마인드": 80.0,
                    "커뮤니케이션": 75.0,
                    "리더십협업": 85.0,
                    "전문성학습": 88.0,
                    "창의혁신": 70.0,
                    "조직적응": 92.0
                },
                "ai_feedback": {
                    "strengths": "뛰어난 업무 수행 능력과 리더십",
                    "improvements": "커뮤니케이션 스킬 향상 필요",
                    "summary": "전반적으로 우수한 성과를 보이는 인재"
                }
            }
        }