import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Created: {path}")

# 1. Database 설정
db_content = """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# SQLite 데이터베이스 URL
DATABASE_URL = "sqlite:///./airiss_v4.db"

# 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 테이블 생성
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 오류: {e}")
"""
create_file('app/db/database.py', db_content)

# 2. Config 설정
config_content = """from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "AIRISS v4.0"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./airiss_v4.db"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3002"]
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: list = [".csv", ".xlsx", ".xls"]
    
    # 분석 설정
    DEFAULT_SAMPLE_SIZE: int = 25
    MAX_SAMPLE_SIZE: int = 1000
    
    # OpenAI 설정
    OPENAI_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_MAX_TOKENS: int = 1200
    
    class Config:
        env_file = ".env"

settings = Settings()
"""
create_file('app/core/config.py', config_content)

# 3. API Router
api_router_content = """from fastapi import APIRouter

# 엔드포인트를 나중에 추가할 예정
api_router = APIRouter()

# 테스트 엔드포인트
@api_router.get("/test")
async def test_endpoint():
    return {"message": "API v1 is working"}
"""
create_file('app/api/v1/api.py', api_router_content)

# 4. 업데이트된 main.py
updated_main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.database import create_tables
from app.api.v1.api import api_router

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시
    logger.info("AIRISS v4.0 서버 시작")
    create_tables()
    yield
    # 종료 시
    logger.info("AIRISS v4.0 서버 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0",
    description="OK금융그룹 AI 기반 직원 성과/역량 스코어링 시스템",
    version="4.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(api_router, prefix=settings.API_V1_STR)

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "AIRISS v4.0 API Server",
        "version": "4.0.0",
        "status": "running"
    }

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "service": "AIRISS Backend"
    }
"""
create_file('app/main.py', updated_main_content)

print("\n✅ 기본 구조 파일들이 생성되었습니다.")
print("\n다음 명령어로 서버를 재시작하세요:")
print("uvicorn app.main:app --reload --port 8001")