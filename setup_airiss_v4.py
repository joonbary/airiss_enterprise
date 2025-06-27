#!/usr/bin/env python3
"""
AIRISS v4.0 프로젝트 구조 자동 생성 스크립트
실행: python setup_airiss_v4.py
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def create_directory_structure():
    """프로젝트 디렉토리 구조 생성"""
    
    # 기본 디렉토리 구조
    directories = [
        # Backend 구조
        "app",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/core",
        "app/core/analyzers",
        "app/core/services",
        "app/core/config",
        "app/db",
        "app/db/repositories",
        "app/models",
        "app/schemas",
        "app/utils",
        "app/middleware",
        
        # Frontend 구조
        "frontend",
        "frontend/src",
        "frontend/public",
        
        # 테스트
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/e2e",
        
        # 기타
        "alembic",
        "scripts",
        "docs",
        "logs",
        "uploads",
        "static",
        "static/fonts",
    ]
    
    print("📁 디렉토리 구조 생성 중...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Python 패키지로 만들기 위한 __init__.py 생성
        if ("app" in directory or "tests" in directory) and not any(
            x in directory for x in ["frontend", "static", "uploads", "logs", "docs", "alembic", "scripts"]
        ):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write('"""AIRISS v4.0 - OK금융그룹 AI HR System"""\n')
    
    print("✅ 디렉토리 구조 생성 완료!")
    return True

def write_file(filename, lines):
    """파일에 내용 쓰기"""
    with open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def create_gitignore():
    """gitignore 파일 생성"""
    lines = [
        "# Python",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".Python",
        "env/",
        "venv/",
        "ENV/",
        ".venv",
        ".env",
        "",
        "# IDE",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "",
        "# Project specific",
        "uploads/",
        "logs/",
        "*.log",
        ".DS_Store",
        "node_modules/",
        "dist/",
        "build/",
        "*.egg-info/",
        ".coverage",
        "htmlcov/",
        ".pytest_cache/",
        "",
        "# Database",
        "*.db",
        "*.sqlite3",
        "postgres_data/"
    ]
    write_file(".gitignore", lines)
    print("✅ .gitignore 생성 완료")

def create_env_example():
    """환경 변수 예제 파일 생성"""
    lines = [
        "# AIRISS v4.0 환경 변수 설정",
        "",
        "# 앱 설정",
        "PROJECT_NAME=AIRISS v4.0",
        "VERSION=4.0.0",
        "DEBUG=False",
        "",
        "# 데이터베이스",
        "POSTGRES_SERVER=localhost",
        "POSTGRES_USER=airiss",
        "POSTGRES_PASSWORD=your_secure_password_here",
        "POSTGRES_DB=airiss_db",
        "",
        "# Redis",
        "REDIS_URL=redis://localhost:6379",
        "",
        "# 보안",
        "SECRET_KEY=your-secret-key-here-change-in-production",
        "",
        "# OpenAI",
        "OPENAI_API_KEY=sk-your-api-key-here",
        "",
        "# CORS",
        'BACKEND_CORS_ORIGINS=["http://localhost:3000"]',
        "",
        "# 파일 업로드",
        "MAX_UPLOAD_SIZE=104857600",
        "UPLOAD_FOLDER=uploads"
    ]
    write_file(".env.example", lines)
    print("✅ .env.example 생성 완료")

def create_readme():
    """README 파일 생성"""
    lines = [
        "# AIRISS v4.0 - OK금융그룹 AI 기반 직원 성과/역량 스코어링 시스템",
        "",
        "## 프로젝트 개요",
        "",
        "AIRISS(AI-based Intelligent Rating & Insight Scoring System)는 OK금융그룹의 전 직원을 대상으로 하는 AI 기반 종합 성과 평가 시스템입니다.",
        "",
        "### 주요 기능",
        "- 8대 영역 기반 다차원 평가",
        "- 텍스트 + 정량 데이터 하이브리드 분석",
        "- OK등급 체계 (OK★★★ ~ OK D)",
        "- OpenAI GPT 기반 상세 피드백",
        "- 실시간 대시보드 및 시각화",
        "- 개인별 성과 조회 및 비교 분석",
        "",
        "## 기술 스택",
        "",
        "### Backend",
        "- FastAPI (Python 3.10+)",
        "- PostgreSQL 14",
        "- Redis 7",
        "- SQLAlchemy 2.0",
        "- Alembic",
        "",
        "### Frontend",
        "- React 18",
        "- TypeScript",
        "- Material-UI",
        "- Chart.js / Recharts",
        "",
        "### DevOps",
        "- Docker & Docker Compose",
        "- GitHub Actions",
        "- Prometheus + Grafana",
        "",
        "## 설치 및 실행",
        "",
        "### 1. 환경 설정",
        "```",
        "cp .env.example .env",
        "# .env 파일 편집하여 환경 변수 설정",
        "```",
        "",
        "### 2. Docker Compose로 실행",
        "```",
        "docker-compose up -d",
        "```",
        "",
        "### 3. 데이터베이스 마이그레이션",
        "```",
        "docker-compose exec backend alembic upgrade head",
        "```",
        "",
        "### 4. 접속",
        "- Frontend: http://localhost:3000",
        "- Backend API: http://localhost:8000",
        "- API Docs: http://localhost:8000/docs",
        "",
        "## 라이센스",
        "",
        "Copyright (c) 2024 OK Financial Group. All rights reserved."
    ]
    write_file("README.md", lines)
    print("✅ README.md 생성 완료")

def create_requirements_txt():
    """requirements.txt 생성"""
    lines = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "alembic==1.12.1",
        "asyncpg==0.29.0",
        "redis==5.0.1",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "pandas==2.1.3",
        "openpyxl==3.1.2",
        "python-multipart==0.0.6",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "email-validator==2.1.0",
        "httpx==0.25.2",
        "openai==1.3.7",
        "prometheus-client==0.19.0",
        "structlog==23.2.0"
    ]
    write_file("requirements.txt", lines)
    print("✅ requirements.txt 생성 완료")

def create_dockerfile():
    """Dockerfile 생성"""
    lines = [
        "FROM python:3.10-slim",
        "",
        "WORKDIR /app",
        "",
        "# 시스템 의존성 설치",
        "RUN apt-get update && apt-get install -y \\",
        "    gcc \\",
        "    g++ \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "",
        "# 의존성 파일 복사",
        "COPY requirements.txt .",
        "",
        "# 의존성 설치",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "",
        "# 애플리케이션 코드 복사",
        "COPY . .",
        "",
        "# 포트 노출",
        "EXPOSE 8000",
        "",
        "# 실행 명령",
        'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]'
    ]
    write_file("Dockerfile", lines)
    print("✅ Dockerfile 생성 완료")

def create_docker_compose():
    """docker-compose.yml 생성"""
    lines = [
        "version: '3.8'",
        "",
        "services:",
        "  postgres:",
        "    image: postgres:14-alpine",
        "    container_name: airiss_postgres",
        "    environment:",
        "      POSTGRES_USER: ${POSTGRES_USER}",
        "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}",
        "      POSTGRES_DB: ${POSTGRES_DB}",
        "    volumes:",
        "      - postgres_data:/var/lib/postgresql/data",
        "    ports:",
        "      - \"5432:5432\"",
        "    healthcheck:",
        "      test: [\"CMD-SHELL\", \"pg_isready -U ${POSTGRES_USER}\"]",
        "      interval: 10s",
        "      timeout: 5s",
        "      retries: 5",
        "",
        "  redis:",
        "    image: redis:7-alpine",
        "    container_name: airiss_redis",
        "    ports:",
        "      - \"6379:6379\"",
        "    healthcheck:",
        "      test: [\"CMD\", \"redis-cli\", \"ping\"]",
        "      interval: 10s",
        "      timeout: 5s",
        "      retries: 5",
        "",
        "  backend:",
        "    build: .",
        "    container_name: airiss_backend",
        "    env_file:",
        "      - .env",
        "    depends_on:",
        "      postgres:",
        "        condition: service_healthy",
        "      redis:",
        "        condition: service_healthy",
        "    ports:",
        "      - \"8000:8000\"",
        "    volumes:",
        "      - ./app:/app/app",
        "      - ./uploads:/app/uploads",
        "      - ./logs:/app/logs",
        "    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload",
        "",
        "volumes:",
        "  postgres_data:"
    ]
    write_file("docker-compose.yml", lines)
    print("✅ docker-compose.yml 생성 완료")

def create_main_app():
    """app/main.py 생성"""
    code = '''"""
AIRISS v4.0 - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 일단 기본 설정으로 시작
app = FastAPI(
    title="AIRISS v4.0",
    version="4.0.0",
    description="OK금융그룹 AI 기반 직원 성과/역량 스코어링 시스템"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 헬스체크
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "4.0.0",
        "service": "AIRISS v4.0"
    }

@app.get("/")
async def root():
    return {"message": "AIRISS v4.0 Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    with open("app/main.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ app/main.py 생성 완료")

def create_config_py():
    """app/core/config.py 생성"""
    code = '''"""
설정 관리 모듈
"""

from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
import secrets

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "AIRISS v4.0"
    VERSION: str = "4.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 보안
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 데이터베이스
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "airiss"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "airiss_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
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
    
    # config 디렉토리가 없으면 생성
    os.makedirs("app/core/config", exist_ok=True)
    
    with open("app/core/config/__init__.py", "w", encoding="utf-8") as f:
        f.write('"""Config module"""\n')
    
    with open("app/core/config/settings.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    print("✅ app/core/config/settings.py 생성 완료")

def main():
    """메인 실행 함수"""
    print("🚀 AIRISS v4.0 프로젝트 설정 시작")
    print("=" * 50)
    
    # 1. 디렉토리 구조 생성
    create_directory_structure()
    
    # 2. 기본 파일들 생성
    create_gitignore()
    create_env_example()
    create_readme()
    create_requirements_txt()
    create_dockerfile()
    create_docker_compose()
    create_main_app()
    create_config_py()
    
    print("\n" + "=" * 50)
    print("🎉 AIRISS v4.0 프로젝트 설정 완료!")
    print("\n다음 단계:")
    print("1. cp .env.example .env")
    print("2. .env 파일을 편집하여 환경 변수 설정")
    print("3. pip install -r requirements.txt")
    print("4. python app/main.py (로컬 테스트)")
    print("5. docker-compose up -d (Docker 사용시)")
    print("\n브라우저에서 http://localhost:8000/docs 접속하여 확인")

if __name__ == "__main__":
    main()