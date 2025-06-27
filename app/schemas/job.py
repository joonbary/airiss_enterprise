"""작업 관련 스키마"""

from pydantic import BaseModel
from typing import List


class JobInfo(BaseModel):
    """작업 정보"""
    job_id: str
    filename: str
    processed: int
    end_time: str
    analysis_mode: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "평가데이터.xlsx",
                "processed": 100,
                "end_time": "2024-01-15 14:30",
                "analysis_mode": "hybrid"
            }
        }


class JobListResponse(BaseModel):
    """작업 목록 응답"""
    jobs: List[JobInfo]