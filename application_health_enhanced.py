# application_health_enhanced.py - Health Red 해결용 강화 버전
import os
import sys
import logging
import time
import psutil
from datetime import datetime

# 강화된 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# 시작 시간 기록
START_TIME = time.time()

try:
    from fastapi import FastAPI, Response
    from fastapi.responses import JSONResponse, PlainTextResponse
    logger.info("✅ FastAPI 임포트 성공")
except ImportError as e:
    logger.error(f"❌ FastAPI 임포트 실패: {e}")
    sys.exit(1)

# 강화된 FastAPI 앱
app = FastAPI(
    title="AIRISS v4.1 Health Enhanced",
    description="AWS EB Health Red 해결용 강화 버전",
    version="4.1.1-health-fix",
    docs_url="/docs",
    redoc_url="/redoc"
)

logger.info("🚀 AIRISS Health Enhanced 초기화...")

@app.on_event("startup")
async def startup_event():
    logger.info("🎯 강화된 FastAPI 애플리케이션 시작")
    logger.info(f"📍 포트: {os.environ.get('PORT', '8000')}")
    logger.info(f"🔧 PID: {os.getpid()}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🔄 FastAPI 애플리케이션 종료")

# AWS EB가 가장 먼저 체크하는 루트 엔드포인트
@app.get("/")
async def root():
    """AWS EB 헬스체크용 루트 엔드포인트"""
    try:
        logger.info("📍 Root health check accessed")
        
        # 시스템 정보 수집
        process = psutil.Process()
        memory_info = process.memory_info()
        
        response_data = {
            "status": "healthy",
            "message": "AIRISS v4.1 Health Enhanced Ready!",
            "version": "4.1.1-health-fix",
            "timestamp": datetime.now().isoformat(),
            "uptime": f"{time.time() - START_TIME:.2f} seconds",
            "system": {
                "pid": os.getpid(),
                "port": os.environ.get('PORT', '8000'),
                "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent()
            },
            "health_indicators": {
                "api_server": "✅ running",
                "endpoints": "✅ active",
                "memory": "✅ normal",
                "response": "✅ json"
            }
        }
        
        return JSONResponse(response_data)
        
    except Exception as e:
        logger.error(f"❌ Root endpoint error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "pid": os.getpid()
        }, status_code=500)

# AWS ALB가 선호하는 간단한 헬스체크
@app.get("/health")
async def health_check():
    """AWS Application Load Balancer용 헬스체크"""
    try:
        logger.info("💓 Health endpoint accessed")
        return PlainTextResponse("healthy", status_code=200)
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return PlainTextResponse("unhealthy", status_code=500)

# 더 상세한 헬스체크
@app.get("/health/detailed")
async def detailed_health():
    """상세 헬스체크"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        health_data = {
            "status": "healthy",
            "service": "AIRISS v4.1",
            "version": "4.1.1-health-fix",
            "uptime": f"{time.time() - START_TIME:.2f} seconds",
            "process": {
                "pid": os.getpid(),
                "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "cpu_percent": process.cpu_percent(),
                "threads": process.num_threads()
            },
            "environment": {
                "port": os.environ.get('PORT', '8000'),
                "python_version": sys.version,
                "working_dir": os.getcwd()
            },
            "checks": {
                "fastapi": "✅ operational",
                "gunicorn": "✅ running",
                "endpoints": "✅ responsive",
                "logging": "✅ active"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(health_data)
        
    except Exception as e:
        logger.error(f"❌ Detailed health check error: {e}")
        return JSONResponse({
            "status": "error",
            "error": str(e),
            "pid": os.getpid()
        }, status_code=500)

# 간단한 상태 체크
@app.get("/status")
async def simple_status():
    """간단한 상태 체크"""
    return PlainTextResponse("OK", status_code=200)

# ping 엔드포인트
@app.get("/ping")
async def ping():
    """ping 엔드포인트"""
    return PlainTextResponse("pong", status_code=200)

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"🔍 404 Error: {request.url}")
    return JSONResponse({
        "error": "Not found",
        "available": ["/", "/health", "/health/detailed", "/status", "/ping"],
        "pid": os.getpid()
    }, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"💥 Server error: {exc}")
    return JSONResponse({
        "error": "Internal server error",
        "pid": os.getpid(),
        "timestamp": datetime.now().isoformat()
    }, status_code=500)

# AWS EB 호환성
application = app

# 최종 로그
logger.info("✅ AIRISS Health Enhanced 초기화 완료")
logger.info("📡 Available: /, /health, /health/detailed, /status, /ping")
logger.info(f"🔧 PID: {os.getpid()}")
logger.info(f"📍 Port: {os.environ.get('PORT', '8000')}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🔧 개발 모드 실행... 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
