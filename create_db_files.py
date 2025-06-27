# create_db_files.py
import os

def create_db_files():
    """데이터베이스 관련 파일들 생성"""
    
    # 1. app/db/base.py - 데이터베이스 연결 설정
    db_base_content = '''"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Base 클래스 생성
Base = declarative_base()

# 전역 변수
engine = None
AsyncSessionLocal = None

async def init_db():
    """데이터베이스 초기화"""
    global engine, AsyncSessionLocal
    
    try:
        from app.core.config.settings import settings
        
        # 비동기 엔진 생성
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True
        )
        
        # 세션 팩토리 생성
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("데이터베이스 연결 성공")
        
        # 테이블 생성 (개발 환경에서만)
        if settings.DEBUG:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("데이터베이스 테이블 생성 완료")
                
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
'''
    
    # 2. app/models/models.py - SQLAlchemy 모델
    models_content = '''"""
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
'''

    # 3. app/db/repositories/base.py - 기본 Repository
    base_repo_content = '''"""
기본 Repository 클래스
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """기본 CRUD 작업을 위한 Repository"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """ID로 단일 레코드 조회"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """모든 레코드 조회 (페이지네이션)"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """새 레코드 생성"""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: uuid.UUID, **kwargs) -> Optional[ModelType]:
        """레코드 업데이트"""
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: uuid.UUID) -> bool:
        """레코드 삭제"""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self) -> int:
        """전체 레코드 수"""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar()
'''

    # 4. app/db/repositories/job_repository.py
    job_repo_content = '''"""
AnalysisJob Repository
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.db.repositories.base import BaseRepository
from app.models.models import AnalysisJob, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession

class JobRepository(BaseRepository[AnalysisJob]):
    """분석 작업 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(AnalysisJob, db)
    
    async def get_with_scores(self, job_id: uuid.UUID) -> Optional[AnalysisJob]:
        """점수 정보와 함께 작업 조회"""
        result = await self.db.execute(
            select(AnalysisJob)
            .options(selectinload(AnalysisJob.scores))
            .where(AnalysisJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_status(self, status: JobStatus) -> List[AnalysisJob]:
        """상태별 작업 조회"""
        result = await self.db.execute(
            select(AnalysisJob).where(AnalysisJob.status == status)
        )
        return list(result.scalars().all())
    
    async def get_completed_jobs(self, limit: int = 50) -> List[AnalysisJob]:
        """완료된 작업 목록 조회"""
        result = await self.db.execute(
            select(AnalysisJob)
            .where(AnalysisJob.status == JobStatus.COMPLETED)
            .order_by(AnalysisJob.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_progress(
        self, 
        job_id: uuid.UUID, 
        processed: int, 
        failed: int = 0
    ) -> None:
        """작업 진행 상황 업데이트"""
        await self.db.execute(
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                processed_records=processed,
                failed_records=failed
            )
        )
        await self.db.commit()
    
    async def complete_job(
        self, 
        job_id: uuid.UUID, 
        average_score: float
    ) -> None:
        """작업 완료 처리"""
        await self.db.execute(
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                average_score=average_score
            )
        )
        await self.db.commit()
'''

    # 5. app/core/config/settings.py 업데이트
    updated_settings_content = '''"""
설정 관리 모듈
"""
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
import secrets

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
    
    # 데이터베이스
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "airiss"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "airiss_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """데이터베이스 URL 생성"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
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

    # 파일 생성
    files = {
        "app/db/base.py": db_base_content,
        "app/models/models.py": models_content,
        "app/db/repositories/base.py": base_repo_content,
        "app/db/repositories/job_repository.py": job_repo_content,
        "app/core/config/settings.py": updated_settings_content
    }
    
    # __init__.py 파일들
    init_files = [
        "app/models/__init__.py",
        "app/db/repositories/__init__.py"
    ]
    
    print("📁 데이터베이스 파일 생성 중...")
    
    for filepath, content in files.items():
        # 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 파일 쓰기
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"✅ {filepath}")
    
    # __init__.py 파일 생성
    for filepath in init_files:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# AIRISS v4.0\n")
        print(f"✅ {filepath}")
    
    print("\n✅ 데이터베이스 파일 생성 완료!")

if __name__ == "__main__":
    create_db_files()