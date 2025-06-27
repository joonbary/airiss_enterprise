from pydantic_settings import BaseSettings
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
