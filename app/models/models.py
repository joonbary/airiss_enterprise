"""
AIRISS v4.0 데이터베이스 모델
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.base import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisMode(str, enum.Enum):
    TEXT = "text"
    QUANTITATIVE = "quantitative"
    HYBRID = "hybrid"

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    
    # 레코드 정보
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    failed_records = Column(Integer, default=0)
    
    # 분석 설정
    analysis_mode = Column(Enum(AnalysisMode), default=AnalysisMode.HYBRID)
    sample_size = Column(Integer)
    enable_ai_feedback = Column(Boolean, default=False)
    
    # 시간 정보
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # 메타데이터
    created_by = Column(String(100))
    metadata = Column(JSON)
    error_message = Column(Text)
    
    # 평균 점수
    average_score = Column(Float)
    
    # 관계
    scores = relationship("EmployeeScore", back_populates="job", cascade="all, delete-orphan")
    file_info = relationship("FileUpload", back_populates="job", uselist=False)

class EmployeeScore(Base):
    __tablename__ = "employee_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id", ondelete="CASCADE"))
    
    # 직원 정보
    employee_uid = Column(String(100), nullable=False, index=True)
    
    # 종합 점수
    hybrid_score = Column(Float, nullable=False)
    text_score = Column(Float)
    quantitative_score = Column(Float)
    confidence_score = Column(Float)
    
    # 등급 정보
    ok_grade = Column(String(20))
    grade_description = Column(String(200))
    percentile_rank = Column(Float)
    
    # 8대 영역 점수 (JSON)
    dimension_scores = Column(JSON)  # {"업무성과": 85.5, "KPI달성": 90.0, ...}
    dimension_details = Column(JSON)  # 상세 분석 정보
    
    # AI 피드백
    ai_strengths = Column(Text)
    ai_improvements = Column(Text)
    ai_feedback = Column(Text)
    ai_processing_time = Column(Float)
    
    # 원본 데이터
    raw_text = Column(Text)
    quantitative_data = Column(JSON)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    analysis_metadata = Column(JSON)
    
    # 관계
    job = relationship("AnalysisJob", back_populates="scores")

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id", ondelete="CASCADE"))
    
    # 파일 정보
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255))
    file_size = Column(Integer)
    file_type = Column(String(50))
    
    # 데이터 정보
    total_rows = Column(Integer)
    total_columns = Column(Integer)
    
    # 컬럼 정보 (JSON)
    uid_columns = Column(JSON)
    opinion_columns = Column(JSON)
    quantitative_columns = Column(JSON)
    all_columns = Column(JSON)
    
    # 업로드 정보
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(100))
    
    # 관계
    job = relationship("AnalysisJob", back_populates="file_info")

# 인덱스 추가를 위한 명시적 정의
from sqlalchemy import Index

# 복합 인덱스
Index('idx_job_status_created', AnalysisJob.status, AnalysisJob.created_at)
Index('idx_score_job_uid', EmployeeScore.job_id, EmployeeScore.employee_uid)
Index('idx_score_grade', EmployeeScore.ok_grade)