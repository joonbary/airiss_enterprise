# application.py - AWS Elastic Beanstalk 최소 버전
import os
import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # 현재 디렉토리를 패스에 추가
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    logger.info("🚀 AIRISS 최소 버전 시작...")
    
    # FastAPI 임포트
    from fastapi import FastAPI
    
    # 최소한의 앱 생성
    app = FastAPI(title="AIRISS v4.1 Minimal")
    
    @app.get("/")
    async def root():
        return {
            "message": "AIRISS v4.1 Minimal Working!",
            "status": "healthy",
            "version": "4.1.0-minimal"
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy", 
            "service": "AIRISS v4.1",
            "components": {
                "fastapi": "running",
                "basic_endpoints": "active"
            }
        }
    
    @app.get("/api")
    async def api_info():
        return {
            "message": "AIRISS v4.1 API",
            "status": "minimal_mode",
            "endpoints": ["/", "/health", "/api"]
        }
    
    # Elastic Beanstalk 호환성
    application = app
    
    logger.info("✅ AIRISS 최소 앱 초기화 완료")
    
except Exception as e:
    logger.error(f"❌ 오류 발생: {e}")
    
    # 완전 폴백 앱
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def emergency():
        return {"status": "emergency_mode", "error": str(e)}
    
    @app.get("/health") 
    async def emergency_health():
        return {"status": "error", "error": str(e)}
    
    application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
