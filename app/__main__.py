"""
AIRISS v4.1 모듈 실행 엔트리포인트
"""
from app.main import app
import uvicorn
import os

if __name__ == "__main__":
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
        reload=False,
        access_log=True
    )
