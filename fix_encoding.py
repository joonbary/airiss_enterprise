import os
import shutil

def create_clean_files():
    # app/__init__.py
    init_content = """# AIRISS v4.0 App Package
"""
    
    # app/main.py
    main_content = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

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
    allow_origins=["http://localhost:3000", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    # 파일 생성
    with open('app/__init__.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(init_content)
    print("Created: app/__init__.py")
    
    with open('app/main.py', 'w', encoding='utf-8', newline='\n') as f:
        f.write(main_content)
    print("Created: app/main.py")
    
    # 추가 필요한 __init__.py 파일들
    dirs_need_init = [
        'app/api',
        'app/api/v1',
        'app/api/v1/endpoints',
        'app/core',
        'app/db',
        'app/models',
        'app/schemas'
    ]
    
    for dir_path in dirs_need_init:
        os.makedirs(dir_path, exist_ok=True)
        init_path = os.path.join(dir_path, '__init__.py')
        with open(init_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(f"# {dir_path} package\n")
        print(f"Created: {init_path}")

if __name__ == "__main__":
    create_clean_files()
    print("\n✅ 모든 파일이 UTF-8로 재생성되었습니다.")