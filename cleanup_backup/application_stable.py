# application.py - AWS Elastic Beanstalk 안정화 버전
import os
import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FastAPI import 먼저 시도
try:
    from fastapi import FastAPI, Response
    from fastapi.responses import JSONResponse
    logger.info("✅ FastAPI 임포트 성공")
except ImportError as e:
    logger.error(f"❌ FastAPI 임포트 실패: {e}")
    sys.exit(1)

# 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Stabilized",
    description="AIRISS v4.1 안정화 버전",
    version="4.1.0-stable"
)

logger.info("🚀 AIRISS v4.1 안정화 버전 초기화...")

# 기본 엔드포인트
@app.get("/")
async def root():
    """기본 루트 엔드포인트"""
    return JSONResponse({
        "message": "AIRISS v4.1 Stabilized Working!",
        "status": "healthy",
        "version": "4.1.0-stable",
        "timestamp": "2025-07-03",
        "endpoints": ["/", "/health", "/api", "/status"]
    })

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        return JSONResponse({
            "status": "healthy",
            "service": "AIRISS v4.1",
            "version": "4.1.0-stable",
            "components": {
                "fastapi": "running",
                "endpoints": "active",
                "database": "not_connected",
                "analysis": "minimal_mode"
            },
            "timestamp": "2025-07-03",
            "uptime": "running"
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500)

@app.get("/api")
async def api_info():
    """API 정보 엔드포인트"""
    return JSONResponse({
        "message": "AIRISS v4.1 API",
        "status": "minimal_mode",
        "version": "4.1.0-stable",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "api_info": "/api",
            "status": "/status"
        },
        "features": {
            "basic_api": True,
            "health_monitoring": True,
            "json_responses": True,
            "error_handling": True
        }
    })

@app.get("/status")
async def status_check():
    """상태 확인 엔드포인트"""
    return JSONResponse({
        "system": "AIRISS v4.1",
        "status": "operational",
        "version": "4.1.0-stable",
        "mode": "minimal",
        "checks": {
            "api_server": "✅ healthy",
            "endpoints": "✅ active",
            "responses": "✅ json",
            "errors": "✅ handled"
        }
    })

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/api", "/status"],
        "requested": str(request.url)
    }, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"Server error: {exc}")
    return JSONResponse({
        "error": "Internal server error",
        "message": "Please try again later"
    }, status_code=500)

# AWS Elastic Beanstalk 호환성
application = app

logger.info("✅ AIRISS v4.1 안정화 버전 초기화 완료")
logger.info("📡 Available endpoints: /, /health, /api, /status")

if __name__ == "__main__":
    import uvicorn
    logger.info("🔧 개발 모드로 실행...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
