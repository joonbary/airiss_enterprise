@'
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FileBase(BaseModel):
    filename: str
    file_size: int
    total_records: int
    column_count: int
    columns: List[str]

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    upload_time: datetime
    status: str
    
    class Config:
        from_attributes = True

class FileList(BaseModel):
    files: List[FileResponse]
    total: int
    skip: int
    limit: int

class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    total_records: int
    columns: List[str]
    uid_columns: List[str]
    opinion_columns: List[str]
    quantitative_columns: List[str]
    status: str
    message: str
'@ | Out-File -FilePath "app/schemas/file.py" -Encoding UTF8