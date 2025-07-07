# EMERGENCY_APPLICATION.PY - 湲닿툒 蹂듦뎄??理쒖냼 踰꾩쟾
import os
import sys
import logging

# 湲곕낯 濡쒓퉭
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
except ImportError as e:
    logger.error(f"FastAPI import failed: {e}")
    sys.exit(1)

# 理쒖냼 ???앹꽦
app = FastAPI(title="AIRISS Emergency Recovery", version="emergency-1.0")

@app.get("/")
async def root():
    return {"status": "emergency_recovery", "message": "AIRISS Emergency Mode"}

@app.get("/health")
async def health():
    return PlainTextResponse("OK", status_code=200)

@app.get("/status") 
async def status():
    return {"status": "emergency", "pid": os.getpid()}

# AWS EB ?명솚??application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
