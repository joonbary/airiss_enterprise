"""상태 확인 관련 스키마"""

from pydantic import BaseModel
from typing import Dict, Any


class StatusResponse(BaseModel):
    """분석 상태 응답"""
    job_id: str
    status: str
    total: int
    processed: int
    failed: int
    progress: float
    processing_time: str
    average_score: float
    error: str
    ai_success_count: int
    ai_fail_count: int
    version: str
    hybrid_analysis_info: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "total": 100,
                "processed": 95,
                "failed": 5,
                "progress": 100.0,
                "processing_time": "2분 35초",
                "average_score": 75.5,
                "error": "",
                "ai_success_count": 90,
                "ai_fail_count": 5,
                "version": "4.0",
                "hybrid_analysis_info": {
                    "quantitative_data_count": 85,
                    "quantitative_usage_rate": 85.0,
                    "analysis_mode": "hybrid"
                }
            }
        }