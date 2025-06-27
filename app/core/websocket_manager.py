# app/core/websocket_manager.py
import asyncio  # ✅ 맨 위로 이동!
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket 연결 관리자 - AIRISS v4.0 실시간 통신 핵심"""
    
    def __init__(self):
        # 클라이언트별 연결 저장
        self.active_connections: Dict[str, WebSocket] = {}
        
        # 채널별 구독자 관리 (향후 확장용)
        self.channel_subscribers: Dict[str, List[str]] = {
            "analysis": [],      # 분석 진행상황 구독
            "alerts": [],        # 실시간 알림 구독
            "dashboard": [],     # 대시보드 업데이트 구독
            "admin": []          # 관리자 전용 채널
        }
        
        # 연결 통계
        self.connection_stats = {
            "total_connections": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "connection_history": []
        }
    
    async def connect(self, websocket: WebSocket, client_id: str, channels: List[str] = None):
        """새로운 WebSocket 연결 수락"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # 채널 구독
        if channels:
            for channel in channels:
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].append(client_id)
        
        # 통계 업데이트
        self.connection_stats["total_connections"] += 1
        self.connection_stats["connection_history"].append({
            "client_id": client_id,
            "connected_at": datetime.now().isoformat(),
            "channels": channels or []
        })
        
        logger.info(f"✅ Client {client_id} connected. Total active: {len(self.active_connections)}")
        
        # 연결 성공 메시지 전송
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "AIRISS v4.0 실시간 시스템에 연결되었습니다.",
            "subscribed_channels": channels or []
        }, client_id)
        
        # 다른 클라이언트들에게 새 연결 알림
        await self.broadcast_to_channel("admin", {
            "type": "user_connected",
            "client_id": client_id,
            "total_connections": len(self.active_connections),
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, client_id: str):
        """WebSocket 연결 종료"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
            # 모든 채널에서 구독 해제
            for channel, subscribers in self.channel_subscribers.items():
                if client_id in subscribers:
                    subscribers.remove(client_id)
            
            logger.info(f"❌ Client {client_id} disconnected. Total active: {len(self.active_connections)}")
            
            # 관리자 채널에 연결 종료 알림
            asyncio.create_task(self.broadcast_to_channel("admin", {
                "type": "user_disconnected",
                "client_id": client_id,
                "total_connections": len(self.active_connections),
                "timestamp": datetime.now().isoformat()
            }))
    
    async def send_personal_message(self, message: dict, client_id: str):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
                self.connection_stats["total_messages_sent"] += 1
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude_client: str = None):
        """모든 연결된 클라이언트에게 메시지 전송"""
        disconnected_clients = []
        
        for client_id, connection in self.active_connections.items():
            if exclude_client and client_id == exclude_client:
                continue
                
            try:
                await connection.send_json(message)
                self.connection_stats["total_messages_sent"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # 연결이 끊긴 클라이언트 정리
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """특정 채널 구독자들에게만 메시지 전송"""
        if channel not in self.channel_subscribers:
            logger.warning(f"Channel {channel} does not exist")
            return
        
        disconnected_clients = []
        
        for client_id in self.channel_subscribers[channel]:
            if client_id in self.active_connections:
                try:
                    await self.active_connections[client_id].send_json(message)
                    self.connection_stats["total_messages_sent"] += 1
                except Exception as e:
                    logger.error(f"Error sending to {client_id} on channel {channel}: {e}")
                    disconnected_clients.append(client_id)
        
        # 연결이 끊긴 클라이언트 정리
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def handle_client_message(self, client_id: str, message: str):
        """클라이언트로부터 받은 메시지 처리"""
        self.connection_stats["total_messages_received"] += 1
        
        try:
            # JSON 메시지 파싱 시도
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            # 메시지 타입별 처리
            if message_type == "subscribe":
                # 채널 구독 요청
                channels = data.get("channels", [])
                for channel in channels:
                    if channel in self.channel_subscribers and client_id not in self.channel_subscribers[channel]:
                        self.channel_subscribers[channel].append(client_id)
                
                await self.send_personal_message({
                    "type": "subscription_confirmed",
                    "channels": channels,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif message_type == "unsubscribe":
                # 채널 구독 해제 요청
                channels = data.get("channels", [])
                for channel in channels:
                    if channel in self.channel_subscribers and client_id in self.channel_subscribers[channel]:
                        self.channel_subscribers[channel].remove(client_id)
                
                await self.send_personal_message({
                    "type": "unsubscription_confirmed",
                    "channels": channels,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif message_type == "ping":
                # 연결 상태 확인
                await self.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            else:
                # 기본 에코 응답
                await self.broadcast({
                    "type": "message",
                    "from": client_id,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }, exclude_client=client_id)
                
        except json.JSONDecodeError:
            # 일반 텍스트 메시지 처리
            await self.broadcast({
                "type": "text_message",
                "from": client_id,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }, exclude_client=client_id)
    
    def get_connection_info(self) -> dict:
        """현재 연결 상태 정보 반환"""
        return {
            "active_connections": len(self.active_connections),
            "connected_clients": list(self.active_connections.keys()),
            "channel_info": {
                channel: len(subscribers) 
                for channel, subscribers in self.channel_subscribers.items()
            },
            "statistics": self.connection_stats
        }
    
    async def send_analysis_progress(self, job_id: str, progress_data: dict):
        """분석 진행상황 전송 - AIRISS 특화 기능"""
        message = {
            "type": "analysis_progress",
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            **progress_data
        }
        await self.broadcast_to_channel("analysis", message)
    
    async def send_alert(self, alert_level: str, message: str, details: dict = None):
        """실시간 알림 전송 - AIRISS 특화 기능"""
        alert_message = {
            "type": "alert",
            "level": alert_level,  # info, warning, error, success
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_channel("alerts", alert_message)
    
    async def send_dashboard_update(self, update_type: str, data: dict):
        """대시보드 업데이트 전송 - AIRISS 특화 기능"""
        update_message = {
            "type": "dashboard_update",
            "update_type": update_type,  # score_change, new_analysis, statistics_update
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_channel("dashboard", update_message)