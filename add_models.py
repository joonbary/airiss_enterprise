import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Created: {path}")

# 1. Job 모델
job_model = """from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON
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
"""
create_file('app/models/job.py', job_model)

# 2. File 모델
file_model = """from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime

from app.db.database import Base

class FileRecord(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer)
    column_count = Column(Integer)
    status = Column(String, default="uploaded")
    metadata = Column(JSON, nullable=True)
"""
create_file('app/models/file.py', file_model)

# 3. Employee Result 모델
employee_model = """from sqlalchemy import Column, String, Float, JSON, ForeignKey
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
    metadata = Column(JSON, nullable=True)
"""
create_file('app/models/employee.py', employee_model)

# 4. models/__init__.py
models_init = """from app.models.job import Job
from app.models.file import FileRecord
from app.models.employee import EmployeeResult

__all__ = ["Job", "FileRecord", "EmployeeResult"]
"""
create_file('app/models/__init__.py', models_init)

print("\n✅ 모든 모델이 생성되었습니다.")