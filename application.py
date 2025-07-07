import os
import logging
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="AIRISS Deploy Test", version="1.0.0")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "AIRISS v4.0 Deploy Success", "status": "running"}

@app.get("/health")
async def health():
    logger.info("Health check accessed")
    return PlainTextResponse("OK", status_code=200)

@app.get("/status")
async def status():
    logger.info("Status endpoint accessed")
    return {
        "status": "healthy",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "version": "1.0.0",
        "port": os.environ.get("PORT", "8000")
    }

# AWS 호환성
application = app

# 개발 서버 실행
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)