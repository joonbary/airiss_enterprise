# app/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

router = APIRouter()

# WebSocket client manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "job_id": job_id,
            "message": f"Connected to job {job_id}",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_progress(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            disconnected = set()
            
            for websocket in self.active_connections[job_id]:
                try:
                    await websocket.send_json(data)
                except:
                    disconnected.add(websocket)
            
            for websocket in disconnected:
                self.disconnect(websocket, job_id)
    
    async def broadcast_to_job(self, job_id: str, message: dict):
        await self.send_progress(job_id, message)

manager = ConnectionManager()

@router.websocket("/ws/analysis/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket, job_id)
    
    try:
        await websocket.send_json({
            "type": "status",
            "job_id": job_id,
            "message": "Waiting for analysis updates...",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        print(f"Client disconnected from job {job_id}")
