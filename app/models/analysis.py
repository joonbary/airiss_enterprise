# app/models/analysis.py
# AIRISS v4.0 분석 관련 데이터 모델

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    file_id: str
    sample_size: int = 10
    analysis_mode: str = "hybrid"  # "text", "quantitative", "hybrid"
    openai_api_key: Optional[str] = None
    enable_ai_feedback: bool = False
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

class AnalysisStatus(BaseModel):
    """분석 상태 모델"""
    job_id: str
    status: str  # "processing", "completed", "failed"
    total: int
    processed: int
    failed: int = 0
    progress: float = 0.0
    processing_time: Optional[str] = None
    average_score: Optional[float] = None
    error: Optional[str] = None
    ai_success_count: Optional[int] = 0
    ai_fail_count: Optional[int] = 0
    version: str = "4.0"
    hybrid_analysis_info: Optional[Dict[str, Any]] = {}

class AnalysisResult(BaseModel):
    """개별 분석 결과 모델"""
    uid: str
    opinion: str
    hybrid_score: float
    text_score: float
    quantitative_score: float
    ok_grade: str
    grade_description: str
    confidence: float
    analysis_timestamp: datetime
    ai_feedback: Optional[Dict[str, Any]] = None
    dimension_scores: Optional[Dict[str, float]] = None

class JobInfo(BaseModel):
    """작업 정보 모델"""
    job_id: str
    file_id: str
    filename: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_records: int
    processed_records: int = 0
    failed_records: int = 0
    analysis_mode: str = "hybrid"
    enable_ai_feedback: bool = False
    result_file_path: Optional[str] = None
    error_message: Optional[str] = None