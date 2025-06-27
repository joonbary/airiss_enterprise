from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON
from datetime import datetime

from app.db.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, index=True)
    file_id = Column(String, nullable=False)
    status = Column(String, default="pending")
    sample_size = Column(Integer)
    analysis_mode = Column(String, default="hybrid")
    enable_ai_feedback = Column(Boolean, default=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    total = Column(Integer, default=0)
    processed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    average_score = Column(Float, nullable=True)
    ai_success_count = Column(Integer, default=0)
    ai_fail_count = Column(Integer, default=0)
    error = Column(String, nullable=True)
    result_file = Column(String, nullable=True)
    hybrid_analysis_info = Column(JSON, nullable=True)
