# app/models/file_upload.py
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.models.base import Base

class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 메타데이터
    total_records = Column(Integer)
    column_count = Column(Integer)
    uid_columns = Column(JSON)  # ['UID', '사번' 등]
    opinion_columns = Column(JSON)  # ['평가의견', 'feedback' 등]
    quantitative_columns = Column(JSON)  # ['점수', '등급' 등]
    
    # 파일 상태
    status = Column(String, default='uploaded')  # uploaded, processing, completed
    error_message = Column(Text)