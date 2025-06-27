# simple_server.py
# AIRISS v4.0 간단한 서버 - 문제 진단용

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import uvicorn

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0 - Simple Test Server",
    description="문제 진단용 간단한 서버",
    version="4.0.0-test"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """기본 엔드포인트"""
    return {
        "message": "AIRISS v4.0 Simple Test Server",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "server": "simple_test",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test_endpoint():
    """테스트용 엔드포인트"""
    try:
        # SQLiteService import 테스트
        from app.db.sqlite_service import SQLiteService
        db_service = SQLiteService()
        
        return {
            "status": "success",
            "sqlite_import": "OK",
            "db_path": db_service.db_path,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("🚀 AIRISS v4.0 Simple Test Server 시작...")
    print("📡 URL: http://localhost:8002")
    print("🔍 테스트: http://localhost:8002/test")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
    except Exception as e:
        print(f"❌ 서버 시작 오류: {e}")
        input("엔터를 눌러 종료...")
