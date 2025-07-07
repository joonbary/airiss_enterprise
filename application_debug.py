# application_debug.py - AWS 배포 디버깅 강화 버전
import os
import sys
import logging
import time
from pathlib import Path

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
start_time = time.time()
logger.info("=" * 50)
logger.info("🚀 AIRISS v4.1 애플리케이션 시작")
logger.info(f"⏰ 시작 시간: {time.ctime()}")
logger.info(f"🐍 Python 버전: {sys.version}")
logger.info(f"📁 현재 디렉토리: {os.getcwd()}")
logger.info(f"🌍 환경변수 PORT: {os.environ.get('PORT', 'NOT_SET')}")
logger.info("=" * 50)

# FastAPI import 시도
try:
    from fastapi import FastAPI, Response, Request
    from fastapi.responses import JSONResponse
    logger.info("✅ FastAPI 임포트 성공")
except ImportError as e:
    logger.error(f"❌ FastAPI 임포트 실패: {e}")
    sys.exit(1)

# 환경변수 체크
port = os.environ.get('PORT')
if not port:
    logger.warning("⚠️ PORT 환경변수가 설정되지 않음")
    port = "8000"
else:
    logger.info(f"✅ PORT 환경변수 설정됨: {port}")

# 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Debug Version",
    description="AWS 배포 디버깅용 버전",
    version="4.1.0-debug"
)

# 미들웨어로 모든 요청 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"📡 요청: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"📤 응답: {response.status_code} (처리시간: {process_time:.3f}s)")
    
    return response

@app.get("/")
async def root():
    """강화된 루트 엔드포인트"""
    logger.info("📋 루트 엔드포인트 호출됨")
    
    return JSONResponse({
        "message": "AIRISS v4.1 Debug Version Working!",
        "status": "healthy",
        "version": "4.1.0-debug",
        "timestamp": time.ctime(),
        "uptime_seconds": round(time.time() - start_time, 2),
        "system_info": {
            "python_version": sys.version.split()[0],
            "current_dir": os.getcwd(),
            "port": os.environ.get('PORT', 'NOT_SET'),
            "environment": os.environ.get('NODE_ENV', 'NOT_SET')
        },
        "endpoints": ["/", "/health", "/debug", "/system"]
    })

@app.get("/health")
async def health_check():
    """상세한 헬스체크"""
    logger.info("🏥 헬스체크 호출됨")
    
    try:
        import psutil
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
    except ImportError:
        cpu_percent = "N/A"
        memory = None
    
    return JSONResponse({
        "status": "healthy",
        "service": "AIRISS v4.1 Debug",
        "version": "4.1.0-debug", 
        "timestamp": time.ctime(),
        "uptime_seconds": round(time.time() - start_time, 2),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_available": f"{memory.available / 1024**3:.2f} GB" if memory else "N/A",
            "memory_percent": f"{memory.percent}%" if memory else "N/A"
        },
        "environment": {
            "PORT": os.environ.get('PORT', 'NOT_SET'),
            "NODE_ENV": os.environ.get('NODE_ENV', 'NOT_SET'),
            "PYTHONPATH": os.environ.get('PYTHONPATH', 'NOT_SET')
        }
    })

@app.get("/debug")
async def debug_info():
    """디버깅 정보"""
    logger.info("🐛 디버그 정보 호출됨")
    
    return JSONResponse({
        "debug_info": {
            "application_file": __file__,
            "python_executable": sys.executable,
            "python_version": sys.version,
            "current_working_directory": os.getcwd(),
            "process_id": os.getpid(),
            "environment_variables": {
                "PORT": os.environ.get('PORT'),
                "PATH": os.environ.get('PATH', '')[:200] + "...",
                "PYTHONPATH": os.environ.get('PYTHONPATH'),
                "NODE_ENV": os.environ.get('NODE_ENV')
            },
            "startup_time": time.ctime(start_time),
            "uptime_seconds": round(time.time() - start_time, 2)
        }
    })

@app.get("/system")
async def system_info():
    """시스템 정보"""
    logger.info("💻 시스템 정보 호출됨")
    
    try:
        import platform
        return JSONResponse({
            "system": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "machine": platform.machine(),
                "node": platform.node()
            },
            "files": {
                "current_dir_files": os.listdir(os.getcwd())[:20],  # 처음 20개만
                "application_exists": os.path.exists("application.py"),
                "requirements_exists": os.path.exists("requirements.txt"),
                "procfile_exists": os.path.exists("Procfile")
            }
        })
    except Exception as e:
        logger.error(f"시스템 정보 오류: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

# 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request, exc):
    logger.warning(f"🔍 404 에러: {request.url}")
    return JSONResponse({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/health", "/debug", "/system"],
        "requested": str(request.url)
    }, status_code=404)

@app.exception_handler(500)
async def server_error_handler(request, exc):
    logger.error(f"💥 서버 에러: {exc}")
    return JSONResponse({
        "error": "Internal server error",
        "message": str(exc),
        "debug": "Check logs for details"
    }, status_code=500)

# AWS Elastic Beanstalk 호환성
application = app

# 애플리케이션 준비 완료 로그
logger.info("✅ AIRISS v4.1 디버그 버전 준비 완료")
logger.info(f"🎯 설정된 포트: {port}")
logger.info("📡 사용 가능한 엔드포인트: /, /health, /debug, /system")
logger.info("🚀 애플리케이션 시작 대기 중...")

if __name__ == "__main__":
    import uvicorn
    port_int = int(port)
    logger.info(f"🔧 개발 모드로 직접 실행... 포트: {port_int}")
    uvicorn.run(app, host="0.0.0.0", port=port_int, log_level="info")
