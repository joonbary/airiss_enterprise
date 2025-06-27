# app/models/analysis_job.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(String, primary_key=True)
    file_id = Column(String, ForeignKey('file_uploads.id'), nullable=False)
    
    # 분석 설정
    sample_size = Column(Integer)
    analysis_mode = Column(String, default='hybrid')
    ai_enabled = Column(Boolean, default=False)
    openai_model = Column(String, default='gpt-3.5-turbo')
    max_tokens = Column(Integer, default=1200)
    
    # 진행 상태
    status = Column(String, nullable=False, default='pending')
    processed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    
    # 시간 정보
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # 결과 요약
    average_score = Column(Float)
    results_summary = Column(JSON)
    error_message = Column(Text)
    
    # v4 추가 필드
    version = Column(String, default='4.0')
    hybrid_stats = Column(JSON)