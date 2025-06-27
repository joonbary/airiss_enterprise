# app/api/v1/endpoints/analysis.py
"""
AIRISS v4.0 분석 API 엔드포인트
실시간 WebSocket 통합
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from app.core import ConnectionManager
from app.services import AnalysisService

router = APIRouter()

# 의존성 주입을 위한 함수
def get_ws_manager():
    """WebSocket 매니저 인스턴스 반환"""
    from app.main import manager
    return manager

def get_analysis_service(ws_manager: ConnectionManager = Depends(get_ws_manager)):
    """분석 서비스 인스턴스 반환"""
    return AnalysisService(ws_manager)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    service: AnalysisService = Depends(get_analysis_service)
):
    """파일 업로드 엔드포인트"""
    try:
        contents = await file.read()
        result = await service.upload_file(contents, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze/{file_id}")
async def start_analysis(
    file_id: str,
    sample_size: int = 10,
    analysis_mode: str = "hybrid",
    enable_ai_feedback: bool = False,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-3.5-turbo",
    max_tokens: int = 1200,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 시작 엔드포인트"""
    try:
        job_id = await service.start_analysis(
            file_id=file_id,
            sample_size=sample_size,
            analysis_mode=analysis_mode,
            enable_ai_feedback=enable_ai_feedback,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            max_tokens=max_tokens
        )
        return {"job_id": job_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{job_id}")
async def get_job_status(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """작업 상태 조회"""
    status = service.get_job_status(job_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status

@router.get("/results/{job_id}")
async def get_results(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
):
    """분석 결과 조회"""
    df = await service.get_analysis_results(job_id)
    if df is None:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다")
    
    return df.to_dict(orient="records")

@router.get("/download/{job_id}")
async def download_results(
    job_id: str,
    format: str = "excel",
    service: AnalysisService = Depends(get_analysis_service)
):
    """결과 다운로드"""
    data = await service.export_results(job_id, format)
    if data is None:
        raise HTTPException(status_code=404, detail="다운로드할 데이터가 없습니다")
    
    if format == "excel":
        return StreamingResponse(
            io.BytesIO(data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id}.xlsx"
            }
        )
    else:
        return StreamingResponse(
            io.BytesIO(data),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=AIRISS_v4_results_{job_id}.csv"
            }
        )