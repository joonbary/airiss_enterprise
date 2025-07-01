# app/api/websocket_enhanced.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set, List, Optional
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EnhancedConnectionManager:
    def __init__(self):
        # 기존 job_id 기반 연결 (하위 호환성)
        self.job_connections: Dict[str, Set[WebSocket]] = {}
        
        # 새로운 채널 기반 연결
        self.channel_connections: Dict[str, Set[WebSocket]] = {}
        self.client_channels: Dict[str, List[str]] = {}
        self.client_websockets: Dict[str, WebSocket] = {}
        
    # 기존 job_id 방식 (하위 호환성 유지)
    async def connect_to_job(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.job_connections:
            self.job_connections[job_id] = set()
        self.job_connections[job_id].add(websocket)
        
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "job_id": job_id,
            "message": f"Connected to job {job_id}",
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Client connected to job {job_id}")
    
    def disconnect_from_job(self, websocket: WebSocket, job_id: str):
        if job_id in self.job_connections:
            self.job_connections[job_id].discard(websocket)
            if not self.job_connections[job_id]:
                del self.job_connections[job_id]
        logger.info(f"Client disconnected from job {job_id}")
    
    # 새로운 채널 방식
    async def connect_to_channels(self, websocket: WebSocket, client_id: str, channels: List[str]):
        await websocket.accept()
        
        # 클라이언트 정보 저장
        self.client_websockets[client_id] = websocket
        self.client_channels[client_id] = channels
        
        # 각 채널에 연결
        for channel in channels:
            if channel not in self.channel_connections:
                self.channel_connections[channel] = set()
            self.channel_connections[channel].add(websocket)
        
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "channels": channels,
            "message": f"Connected to channels: {', '.join(channels)}",
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"Client {client_id} connected to channels: {channels}")
    
    def disconnect_from_channels(self, client_id: str):
        if client_id in self.client_channels:
            channels = self.client_channels[client_id]
            websocket = self.client_websockets.get(client_id)
            
            # 각 채널에서 연결 해제
            for channel in channels:
                if channel in self.channel_connections and websocket:
                    self.channel_connections[channel].discard(websocket)
                    if not self.channel_connections[channel]:
                        del self.channel_connections[channel]
            
            # 클라이언트 정보 정리
            del self.client_channels[client_id]
            if client_id in self.client_websockets:
                del self.client_websockets[client_id]
            
            logger.info(f"Client {client_id} disconnected from channels: {channels}")
    
    # 진행 상황 전송 (기존 방식)
    async def send_progress_to_job(self, job_id: str, data: dict):
        if job_id in self.job_connections:
            disconnected = set()
            
            for websocket in self.job_connections[job_id]:
                try:
                    await websocket.send_json(data)
                except Exception as e:
                    logger.error(f"Failed to send data to job {job_id}: {e}")
                    disconnected.add(websocket)
            
            for websocket in disconnected:
                self.disconnect_from_job(websocket, job_id)
    
    # 채널로 메시지 브로드캐스트
    async def broadcast_to_channel(self, channel: str, data: dict):
        if channel in self.channel_connections:
            disconnected = set()
            
            message = {
                **data,
                "channel": channel,
                "timestamp": datetime.now().isoformat()
            }
            
            for websocket in self.channel_connections[channel]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send data to channel {channel}: {e}")
                    disconnected.add(websocket)
            
            # 연결이 끊어진 웹소켓 정리
            for websocket in disconnected:
                self.channel_connections[channel].discard(websocket)
                # 클라이언트 ID 찾아서 정리
                for client_id, ws in list(self.client_websockets.items()):
                    if ws == websocket:
                        self.disconnect_from_channels(client_id)
                        break
    
    # 특정 클라이언트에게 메시지 전송
    async def send_to_client(self, client_id: str, data: dict):
        if client_id in self.client_websockets:
            websocket = self.client_websockets[client_id]
            try:
                message = {
                    **data,
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send data to client {client_id}: {e}")
                self.disconnect_from_channels(client_id)
    
    # 연결 상태 확인
    def get_connection_stats(self):
        return {
            "job_connections": {job_id: len(connections) for job_id, connections in self.job_connections.items()},
            "channel_connections": {channel: len(connections) for channel, connections in self.channel_connections.items()},
            "total_clients": len(self.client_websockets)
        }

# 전역 매니저 인스턴스
manager = EnhancedConnectionManager()

# 기존 엔드포인트 (하위 호환성)
@router.websocket("/ws/analysis/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect_to_job(websocket, job_id)
    
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
        manager.disconnect_from_job(websocket, job_id)
    except Exception as e:
        logger.error(f"WebSocket job endpoint error: {e}")
        manager.disconnect_from_job(websocket, job_id)

# 새로운 채널 기반 엔드포인트
@router.websocket("/ws/{client_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket, 
    client_id: str,
    channels: Optional[str] = Query(default="analysis,alerts")
):
    try:
        channel_list = [ch.strip() for ch in channels.split(',') if ch.strip()]
        await manager.connect_to_channels(websocket, client_id, channel_list)
        
        # 연결 확인 메시지
        await websocket.send_json({
            "type": "ready",
            "client_id": client_id,
            "channels": channel_list,
            "message": "WebSocket connection ready",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            try:
                data = await websocket.receive_text()
                
                # 메시지 파싱 시도
                try:
                    message = json.loads(data)
                    message_type = message.get("type", "unknown")
                    
                    if message_type == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif message_type == "subscribe":
                        # 채널 구독 추가
                        new_channel = message.get("channel")
                        if new_channel and new_channel not in channel_list:
                            channel_list.append(new_channel)
                            if new_channel not in manager.channel_connections:
                                manager.channel_connections[new_channel] = set()
                            manager.channel_connections[new_channel].add(websocket)
                            manager.client_channels[client_id] = channel_list
                            
                            await websocket.send_json({
                                "type": "subscribed",
                                "channel": new_channel,
                                "message": f"Subscribed to {new_channel}",
                                "timestamp": datetime.now().isoformat()
                            })
                    
                except json.JSONDecodeError:
                    # 단순 텍스트 메시지 처리
                    if data == "ping":
                        await websocket.send_text("pong")
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing message from {client_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket channel endpoint error: {e}")
    finally:
        manager.disconnect_from_channels(client_id)

# 연결 상태 조회 엔드포인트
@router.get("/ws/status")
async def websocket_status():
    return {
        "status": "active",
        "connections": manager.get_connection_stats(),
        "timestamp": datetime.now().isoformat()
    }

# 매니저 인스턴스 내보내기 (다른 모듈에서 사용)
def get_websocket_manager():
    return manager
