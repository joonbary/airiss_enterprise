from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class EmployeeResult(Base):
    __tablename__ = "employee_results"
    
    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    uid = Column(String, index=True)
    overall_score = Column(Float)
    grade = Column(String)
    text_score = Column(Float)
    quantitative_score = Column(Float)
    confidence = Column(Float)
    dimension_scores = Column(JSON)
    ai_feedback = Column(JSON, nullable=True)
    employee_metadata = Column(JSON, nullable=True)  # metadata -> employee_metadata로 변경
