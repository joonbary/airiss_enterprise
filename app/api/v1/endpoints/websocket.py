# app/api/v1/endpoints/websocket.py
"""
WebSocket 엔드포인트 - 실시간 분석 진행률 스트리밍
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import json
from datetime import datetime

from app.core.websocket_manager import manager
from app.db.database import SessionLocal
from app.models.job import Job

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, job_id: Optional[str] = Query(None)):
    """
    WebSocket 연결 엔드포인트
    
    Query Parameters:
    - job_id: 특정 작업 구독 (선택사항)
    
    메시지 형식:
    {
        "type": "progress_update" | "analysis_complete" | "error",
        "job_id": "작업ID",
        "status": "processing" | "completed" | "failed",
        "processed": 10,
        "total": 100,
        "progress": 10.0,
        "current_employee": "EMP001",
        "timestamp": "2024-01-01T12:00:00"
    }
    """
    await manager.connect(websocket, job_id)
    
    try:
        # 연결 성공 메시지
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"AIRISS v4.0 실시간 연결 성공",
            "job_id": job_id
        }))
        
        # job_id가 제공된 경우 현재 상태 전송
        if job_id:
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    await websocket.send_text(json.dumps({
                        "type": "current_status",
                        "job_id": job_id,
                        "status": job.status,
                        "processed": job.processed,
                        "total": job.total,
                        "progress": round((job.processed / job.total * 100) if job.total > 0 else 0, 1)
                    }))
            finally:
                db.close()
        
        # 연결 유지 및 메시지 수신
        while True:
            data = await websocket.receive_text()
            
            # 클라이언트에서 오는 메시지 처리 (ping/pong 등)
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif message.get("type") == "subscribe" and message.get("job_id"):
                # 새로운 job 구독
                new_job_id = message["job_id"]
                if job_id != new_job_id:
                    manager.disconnect(websocket, job_id)
                    job_id = new_job_id
                    await manager.connect(websocket, job_id)
                    
                    await websocket.send_text(json.dumps({
                        "type": "subscription_changed",
                        "job_id": job_id,
                        "message": f"Job {job_id} 구독 시작"
                    }))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        logger.info(f"WebSocket 정상 종료 - Job ID: {job_id}")
        
    except Exception as e:
        manager.disconnect(websocket, job_id)
        logger.error(f"WebSocket 오류: {e}")