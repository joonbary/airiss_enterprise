# update_for_sqlite.py
import os

def update_for_sqlite():
    """SQLite를 사용하도록 설정 업데이트"""
    
    # 1. app/core/config/settings.py 수정
    settings_content = '''"""
설정 관리 모듈
"""
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import secrets
import os

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "AIRISS v4.0"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # 보안
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 데이터베이스 선택
    USE_SQLITE: bool = True  # 개발 환경에서 SQLite 사용
    
    # PostgreSQL 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "airiss"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "airiss_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """데이터베이스 URL 생성"""
        if self.USE_SQLITE:
            # SQLite URL (비동기)
            return "sqlite+aiosqlite:///./airiss.db"
        else:
            # PostgreSQL URL (비동기)
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """동기 데이터베이스 URL (Alembic용)"""
        if self.USE_SQLITE:
            return "sqlite:///./airiss.db"
        else:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1200
    
    # 파일 업로드
    UPLOAD_FOLDER: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
    
    # 로깅
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
'''

    # 2. app/models/models.py 수정 (SQLite 호환성)
    models_content = '''"""
AIRISS v4.0 데이터베이스 모델
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgreUUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from app.db.base import Base

# SQLite와 PostgreSQL 호환성을 위한 UUID 처리
try:
    from sqlalchemy.dialects.postgresql import UUID
except ImportError:
    # SQLite용 대체
    from sqlalchemy import String as UUID
    
def get_uuid_column():
    """데이터베이스에 따른 UUID 컬럼 타입 반환"""
    from app.core.config.settings import settings
    if settings.USE_SQLITE:
        return String(36)
    else:
        return PostgreUUID(as_uuid=True)

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
    
    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
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
    
    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(get_uuid_column(), ForeignKey("analysis_jobs.id", ondelete="CASCADE"))
    
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
    dimension_scores = Column(JSON)
    dimension_details = Column(JSON)
    
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
    
    id = Column(get_uuid_column(), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(get_uuid_column(), ForeignKey("analysis_jobs.id", ondelete="CASCADE"))
    
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
'''

    # 3. alembic/env.py 업데이트
    alembic_env_content = '''"""Alembic environment configuration."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import your models' Base
from app.db.base import Base
from app.models.models import *  # Import all models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Get database URL from environment or settings
def get_database_url():
    """Get database URL from settings or environment"""
    try:
        from app.core.config.settings import settings
        return settings.SYNC_DATABASE_URL  # Use sync URL for Alembic
    except:
        # Fallback to environment variable
        return os.getenv(
            "DATABASE_URL",
            "sqlite:///./airiss.db"
        )

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_database_url()
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url
    
    # SQLite specific settings
    if "sqlite" in url:
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {}
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True  # SQLite compatibility
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    # 파일 쓰기
    print("📝 SQLite 설정 업데이트 중...")
    
    files = {
        "app/core/config/settings.py": settings_content,
        "app/models/models.py": models_content,
        "alembic/env.py": alembic_env_content
    }
    
    for filepath, content in files.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ {filepath}")
    
    print("\n✅ SQLite 설정 완료!")

if __name__ == "__main__":
    update_for_sqlite()