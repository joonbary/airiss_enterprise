from pydantic import BaseModel
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
