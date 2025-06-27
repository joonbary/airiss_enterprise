"""
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