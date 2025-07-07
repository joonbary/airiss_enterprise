# AIRISS Emergency Recovery Application - Clean English Version
import os
import sys
import logging
from datetime import datetime

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, PlainTextResponse
    logger.info("FastAPI imported successfully")
except ImportError as e:
    logger.error(f"FastAPI import failed: {e}")
    sys.exit(1)

# Create minimal FastAPI application
app = FastAPI(
    title="AIRISS Emergency Recovery",
    version="emergency-1.0",
    description="Emergency recovery mode for AIRISS system"
)

@app.get("/")
async def root():
    """Root endpoint for basic connectivity test"""
    return {
        "status": "emergency_recovery",
        "message": "AIRISS Emergency Mode Active",
        "timestamp": datetime.now().isoformat(),
        "version": "emergency-1.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint for AWS Load Balancer"""
    return PlainTextResponse("OK", status_code=200)

@app.get("/status")
async def status():
    """Detailed status endpoint"""
    return {
        "status": "emergency",
        "mode": "recovery",
        "pid": os.getpid(),
        "timestamp": datetime.now().isoformat(),
        "health": "OK"
    }

@app.get("/info")
async def info():
    """Basic system information"""
    return {
        "system": "AIRISS",
        "mode": "emergency_recovery",
        "environment": os.environ.get("ENVIRONMENT", "production"),
        "port": os.environ.get("PORT", "8000"),
        "python_version": sys.version,
        "uptime": "active"
    }

# AWS Elastic Beanstalk compatibility
application = app

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting emergency server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
