from sqlalchemy import Column, String, Integer, DateTime, JSON
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
    file_metadata = Column(JSON, nullable=True)  # metadata -> file_metadata로 변경
