import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Created: {path}")

# 1. Upload 스키마
upload_schema = """from pydantic import BaseModel
from typing import List, Dict, Any

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    total_records: int
    column_count: int
    uid_columns: List[str]
    opinion_columns: List[str]
    quantitative_columns: List[str]
    airiss_ready: bool
    hybrid_ready: bool
    data_quality: Dict[str, Any]
"""
create_file('app/schemas/upload.py', upload_schema)

# 2. Analysis 스키마
analysis_schema = """from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    file_id: str
    sample_size: int = 25
    analysis_mode: str = "hybrid"
    enable_ai_feedback: bool = False
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1200

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    message: str
    ai_feedback_enabled: bool
    analysis_mode: str
"""
create_file('app/schemas/analysis.py', analysis_schema)

# 3. Status 스키마
status_schema = """from pydantic import BaseModel
from typing import Dict, Any, Optional

class StatusResponse(BaseModel):
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
"""
create_file('app/schemas/status.py', status_schema)

# 4. Employee 스키마
employee_schema = """from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class EmployeeSearchRequest(BaseModel):
    uid: Optional[str] = None
    grade: Optional[str] = None

class EmployeeResponse(BaseModel):
    employee: Dict[str, Any]
    statistics: Dict[str, Any]
"""
create_file('app/schemas/employee.py', employee_schema)

# 5. Job 스키마
job_schema = """from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobResponse(BaseModel):
    job_id: str
    filename: str
    processed: int
    end_time: Optional[str]
    analysis_mode: str
"""
create_file('app/schemas/job.py', job_schema)

# 6. schemas/__init__.py
schemas_init = """from app.schemas.upload import UploadResponse
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.status import StatusResponse
from app.schemas.employee import EmployeeResponse, EmployeeSearchRequest
from app.schemas.job import JobResponse

__all__ = [
    "UploadResponse",
    "AnalysisRequest",
    "AnalysisResponse", 
    "StatusResponse",
    "EmployeeResponse",
    "EmployeeSearchRequest",
    "JobResponse"
]
"""
create_file('app/schemas/__init__.py', schemas_init)

print("\n✅ 모든 스키마가 생성되었습니다.")