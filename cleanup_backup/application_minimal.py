# application_minimal.py - 최소한의 안정 버전
import os
from fastapi import FastAPI

app = FastAPI(title="AIRISS Minimal")

@app.get("/")
def root():
    return {"message": "AIRISS Minimal Working", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "minimal"}

# AWS EB 호환성
application = app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)