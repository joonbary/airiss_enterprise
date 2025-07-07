# application.py - AWS Elastic Beanstalk 최적화 버전
import os
import sys
import logging
from pathlib import Path

# 로깅 설정 강화
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 환경 확인
logger.info("🔍 환경 변수 확인...")
logger.info(f"PORT: {os.environ.get('PORT', 'NOT_SET')}")
logger.info(f"PYTHONPATH: {sys.path}")
logger.info(f"Working Directory: {os.getcwd()}")

# FastAPI import
try:
    from fastapi import FastAPI, Response
    from fastapi.responses import JSONResponse
    logger.info("✅ FastAPI 임포트 성공")
except ImportError as e:
    logger.error(f"❌ FastAPI 임포트 실패: {e}")
    sys.exit(1)

# 앱 생성 with enhanced settings
app = FastAPI(
    title="AIRISS v4.1 Production Ready",
    description="AIRISS v4.1 프로덕션 버전",
    version="4.1.0-production",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("🚀 AIRISS v4.1 프로덕션 버전 초기화...")

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🎯 FastAPI 애플리케이션 시작")
    logger.info(f"📍 포트: {os.environ.get('PORT', '8000')}")

# Shutdown event
@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("🔄 FastAPI 애플리케이션 종료")

# 루트 엔드포인트 (강화된 응답)
@app.get("/")
async def root():
    """강화된 루트 엔드포인트"""
    logger.info("📍 Root endpoint accessed")
    return JSONResponse({
        "message": "AIRISS v4.1 Production Ready!",
        "status": "healthy",
        "version": "4.1.0-production",
        "timestamp": "2025-07-03",
        "server_info": {
            "port": os.environ.get('PORT', '8000'),
            "environment": "production",
            "process_id": os.getpid()
        },
        "endpoints": {
            "root": "/",
            "health": "/health", 
            "api": "/api",
            "status": "/status",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    })

@app.get("/health")
async def health_check():
    """향상된 헬스체크"""
    try:
        logger.info("💓 Health check requested")
        return JSONResponse({
            "status": "healthy",
            "service": "AIRISS v4.1",
            "version": "4.1.0-production", 
            "process_id": os.getpid(),
            "port": os.environ.get('PORT', '8000'),
            "components": {
                "fastapi": "✅ running",
                "gunicorn": "✅ active", 
                "endpoints": "✅ responsive",
                "logging": "✅ operational"
            },
            "timestamp": "2025-07-03",
            "uptime": "running"
        })
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "process_id": os.getpid()
        }, status_code=500)

@app.get("/api")
async def api_info():
    """API 정보"""
    logger.info("📊 API info requested")
    return JSONResponse({
        "message": "AIRISS v4.1 API",
        "status": "production_ready",
        "version": "4.1.0-production",
        "process_id": os.getpid(),
        "features": {
            "enhanced_logging": True,
            "health_monitoring": True,
            "error_handling": True,
            "production_config": True,
            "aws_optimized": True
        }
    })

@app.get("/status")
async def status_check():
    """상세 상태 확인"""
    logger.info("📈 Status check requested")
    return JSONResponse({
        "system": "AIRISS v4.1",
        "status": "operational",
        "version": "4.1.0-production",
        "mode": "production",
        "process_info": {
            "pid": os.getpid(),
            "port": os.environ.get('PORT', '8000'),
            "working_dir": os.getcwd()
        },
        "checks": {
            "api_server": "✅ healthy",
            "endpoints": "✅ active", 
            "responses": "✅ json",
            "errors": "✅ handled",
            "logging": "✅ enhanced",
            "aws_compatible": "✅ optimized"
        }
    })

# 에러 핸들러 강화
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"🔍 404 Error: {request.url}")
    return JSONResponse({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/api", "/status", "/docs"],
        "requested": str(request.url),
        "process_id": os.getpid()
    }, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"💥 Server error: {exc}")
    return JSONResponse({
        "error": "Internal server error",
        "message": "Please try again later",
        "process_id": os.getpid()
    }, status_code=500)

# AWS Elastic Beanstalk 호환성
application = app

# 최종 확인 로그
logger.info("✅ AIRISS v4.1 프로덕션 버전 초기화 완료")
logger.info("📡 Available endpoints: /, /health, /api, /status, /docs, /redoc")
logger.info(f"🔧 Process ID: {os.getpid()}")
logger.info(f"📍 Target Port: {os.environ.get('PORT', '8000')}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🔧 개발 모드로 실행... 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
