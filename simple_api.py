# simple_api.py
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import io
import uuid
import asyncio
from typing import Optional

app = FastAPI(
    title="AIRISS v4.0 Simple",
    description="간단한 테스트 버전",
    version="4.0.0"
)

# 임시 저장소
file_storage = {}
analysis_jobs = {}

@app.get("/")
async def root():
    return {"message": "AIRISS v4.0 Simple API"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드"""
    try:
        contents = await file.read()
        
        # 간단한 파일 정보 저장
        file_id = str(uuid.uuid4())
        file_storage[file_id] = {
            "filename": file.filename,
            "size": len(contents)
        }
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "message": "업로드 성공"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class AnalysisRequest(BaseModel):
    file_id: str
    sample_size: int = 10

@app.post("/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """분석 시작"""
    if request.file_id not in file_storage:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    job_id = str(uuid.uuid4())
    analysis_jobs[job_id] = {
        "status": "processing",
        "progress": 0
    }
    
    # 간단한 백그라운드 작업
    background_tasks.add_task(simple_analysis, job_id)
    
    return {"job_id": job_id, "status": "started"}

async def simple_analysis(job_id: str):
    """간단한 분석 시뮬레이션"""
    for i in range(10):
        await asyncio.sleep(1)
        analysis_jobs[job_id]["progress"] = (i + 1) * 10
    
    analysis_jobs[job_id]["status"] = "completed"
    analysis_jobs[job_id]["progress"] = 100

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """상태 확인"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다")
    
    return analysis_jobs[job_id]