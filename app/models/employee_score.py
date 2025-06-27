# app/models/employee_score.py
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class EmployeeScore(Base):
    __tablename__ = "employee_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey('analysis_jobs.id'), nullable=False)
    
    # 직원 정보
    uid = Column(String, nullable=False, index=True)
    original_opinion = Column(Text)
    
    # 종합 점수 (하이브리드)
    hybrid_score = Column(Float)
    ok_grade = Column(String)  # OK★★★, OK★★, OK★, OK A, OK B+, OK B, OK C, OK D
    percentile = Column(String)  # 상위 X%
    confidence = Column(Float)
    
    # 텍스트 분석 점수
    text_overall_score = Column(Float)
    text_grade = Column(String)
    
    # 정량 분석 점수
    quant_overall_score = Column(Float)
    quant_confidence = Column(Float)
    quant_data_quality = Column(String)  # 높음, 중간, 낮음, 없음
    quant_data_count = Column(Integer)
    
    # 8대 영역별 점수
    dimension_scores = Column(JSON)  # {업무성과: 85, KPI달성: 90, ...}
    dimension_details = Column(JSON)  # 각 영역별 상세 분석
    
    # AI 피드백
    ai_strengths = Column(Text)
    ai_improvements = Column(Text)
    ai_feedback = Column(Text)
    ai_processing_time = Column(Float)
    
    # 메타데이터
    analysis_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    analysis_version = Column(String, default='AIRISS v4.0')
    
    # 인덱스
    __table_args__ = (
        {'extend_existing': True}
    )