# AIRISS v4.0 Standalone Server - 단독 실행 가능 버전
# 모든 의존성을 제거하고 WebSocket 실시간 기능만 제공

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import os
import uvicorn
from typing import Dict, List
from datetime import datetime
import json
import asyncio

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))
WS_HOST = os.getenv("WS_HOST", "localhost")

# 🔌 WebSocket 연결 관리자 (내장)
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_channels: Dict[str, List[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, channels: List[str] = None):
        """클라이언트 연결 및 채널 구독"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_channels[client_id] = channels or ["general"]
        
        logger.info(f"✅ Client {client_id} connected. Channels: {channels}")
        
        # 환영 메시지
        await self.send_personal_message({
            "type": "welcome",
            "message": f"AIRISS v4.0에 연결되었습니다!",
            "client_id": client_id,
            "channels": channels,
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    def disconnect(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_channels:
            del self.client_channels[client_id]
        logger.info(f"❌ Client {client_id} disconnected")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """개별 클라이언트에게 메시지 전송"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_channel(self, message: dict, channel: str = "general"):
        """특정 채널의 모든 클라이언트에게 브로드캐스트"""
        disconnected = []
        for client_id, channels in self.client_channels.items():
            if channel in channels:
                try:
                    await self.active_connections[client_id].send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to {client_id}: {e}")
                    disconnected.append(client_id)
        
        # 연결이 끊어진 클라이언트 정리
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def handle_client_message(self, client_id: str, message: str):
        """클라이언트 메시지 처리"""
        try:
            data = json.loads(message)
            msg_type = data.get("type", "unknown")
            
            if msg_type == "ping":
                await self.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            elif msg_type == "analysis_status":
                # 분석 상태 요청 처리
                await self.send_personal_message({
                    "type": "analysis_status",
                    "status": "ready",
                    "message": "AIRISS v4.0 실시간 모니터링 준비 완료",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            
            else:
                # 에코 응답
                await self.send_personal_message({
                    "type": "echo",
                    "original": data,
                    "timestamp": datetime.now().isoformat()
                }, client_id)
                
        except json.JSONDecodeError:
            # 일반 텍스트 메시지 처리
            await self.send_personal_message({
                "type": "echo",
                "original": message,
                "timestamp": datetime.now().isoformat()
            }, client_id)
    
    def get_connection_info(self):
        """연결 정보 반환"""
        return {
            "total_connections": len(self.active_connections),
            "connected_clients": list(self.active_connections.keys()),
            "channels": dict(self.client_channels)
        }

# WebSocket 연결 관리자 인스턴스
manager = ConnectionManager()

# 🚀 시작/종료 이벤트 처리
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.0 Standalone Server Starting")
    logger.info(f"📡 HTTP: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📡 WebSocket: ws://{WS_HOST}:{SERVER_PORT}/ws/{{client_id}}")
    logger.info(f"🧪 Test WebSocket: ws://{WS_HOST}:{SERVER_PORT}/test-ws")
    logger.info(f"📊 Real-time Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info("🔧 모든 의존성 제거, 단독 실행 가능")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.0 Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0 Standalone",
    description="AI-based Resource Intelligence Scoring System - WebSocket Only",
    version="4.0.0-standalone",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "AIRISS v4.0 Standalone Server",
        "version": "4.0.0-standalone",
        "status": "running",
        "websocket_endpoints": {
            "main": f"ws://{WS_HOST}:{SERVER_PORT}/ws/{{client_id}}",
            "test": f"ws://{WS_HOST}:{SERVER_PORT}/test-ws"
        },
        "connection_info": manager.get_connection_info(),
        "features": [
            "WebSocket 실시간 통신",
            "다중 클라이언트 지원", 
            "채널 기반 메시징",
            "실시간 대시보드",
            "완전 독립 실행"
        ]
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "version": "4.0.0-standalone",
        "timestamp": datetime.now().isoformat(),
        "connections": len(manager.active_connections)
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    """메인 WebSocket 엔드포인트"""
    logger.info(f"🔌 WebSocket connection attempt from: {client_id}")
    
    # 채널 파싱
    channel_list = channels.split(",") if channels else ["general"]
    
    try:
        # 연결 수락 및 채널 구독
        await manager.connect(websocket, client_id, channel_list)
        
        # 메시지 수신 대기
        while True:
            message = await websocket.receive_text()
            await manager.handle_client_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

@app.websocket("/test-ws")
async def test_websocket(websocket: WebSocket):
    """간단한 테스트용 WebSocket"""
    logger.info("🧪 Test WebSocket connection attempt")
    await websocket.accept()
    
    # 환영 메시지
    await websocket.send_json({
        "type": "welcome",
        "message": "AIRISS v4.0 Test WebSocket Connected!",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Test received: {data}")
            
            await websocket.send_json({
                "type": "echo",
                "original": data,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        logger.info("🧪 Test WebSocket disconnected")

@app.get("/dashboard", response_class=HTMLResponse)
async def realtime_dashboard():
    """실시간 대시보드 페이지"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIRISS v4.0 실시간 대시보드</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                text-align: center;
            }}
            
            .header h1 {{
                color: #333;
                font-size: 2.5rem;
                margin-bottom: 10px;
            }}
            
            .card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }}
            
            .status {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9rem;
            }}
            
            .status.connected {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status.disconnected {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            button {{
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                background: #667eea;
                color: white;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
            }}
            
            button:hover {{
                background: #5a67d8;
                transform: translateY(-2px);
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 20px;
            }}
            
            .message-log {{
                background: #2d3748;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                height: 300px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }}
            
            .message-entry {{
                margin-bottom: 8px;
                padding: 4px 0;
                border-bottom: 1px solid #4a5568;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 AIRISS v4.0 실시간 대시보드</h1>
                <div class="subtitle">WebSocket 실시간 모니터링 시스템</div>
                <div style="margin-top: 15px;">
                    <span class="status disconnected" id="connectionStatus">연결 대기 중...</span>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>🔌 연결 제어</h2>
                    <button onclick="connectWebSocket()">연결</button>
                    <button onclick="disconnectWebSocket()">연결 해제</button>
                    <button onclick="sendTestMessage()">테스트 메시지</button>
                    <button onclick="clearLog()">로그 초기화</button>
                </div>
                
                <div class="card">
                    <h2>📊 연결 정보</h2>
                    <div id="connectionInfo">
                        <p>클라이언트 ID: <span id="clientId">-</span></p>
                        <p>연결 시간: <span id="connectionTime">-</span></p>
                        <p>채널: <span id="channels">analysis, alerts</span></p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>📝 실시간 메시지 로그</h2>
                <div class="message-log" id="messageLog">
                    <div class="message-entry">🎯 AIRISS v4.0 실시간 대시보드 준비 완료</div>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let clientId = 'dashboard-' + Math.random().toString(36).substr(2, 9);
            let connectionTime = null;
            
            document.getElementById('clientId').textContent = clientId;
            
            function updateConnectionStatus(connected) {{
                const statusEl = document.getElementById('connectionStatus');
                if (connected) {{
                    statusEl.className = 'status connected';
                    statusEl.textContent = '✅ 연결됨';
                    connectionTime = new Date();
                    document.getElementById('connectionTime').textContent = connectionTime.toLocaleTimeString();
                }} else {{
                    statusEl.className = 'status disconnected';
                    statusEl.textContent = '❌ 연결 끊김';
                    document.getElementById('connectionTime').textContent = '-';
                }}
            }}
            
            function addLogMessage(message, type = 'info') {{
                const logEl = document.getElementById('messageLog');
                const entry = document.createElement('div');
                entry.className = 'message-entry';
                
                const timestamp = new Date().toLocaleTimeString();
                entry.innerHTML = `<strong>[${{timestamp}}]</strong> ${{message}}`;
                
                logEl.appendChild(entry);
                logEl.scrollTop = logEl.scrollHeight;
            }}
            
            function connectWebSocket() {{
                const wsUrl = `ws://{WS_HOST}:{SERVER_PORT}/ws/${{clientId}}`;
                addLogMessage(`🔌 연결 시도: ${{wsUrl}}`);
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {{
                    updateConnectionStatus(true);
                    addLogMessage('✅ WebSocket 연결 성공!', 'success');
                }};
                
                ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    addLogMessage(`📨 수신: ${{data.type}} - ${{data.message || JSON.stringify(data)}}`, 'received');
                }};
                
                ws.onerror = (error) => {{
                    addLogMessage(`❌ WebSocket 오류: ${{error}}`, 'error');
                }};
                
                ws.onclose = () => {{
                    updateConnectionStatus(false);
                    addLogMessage('🔌 WebSocket 연결 종료', 'info');
                }};
            }}
            
            function disconnectWebSocket() {{
                if (ws) {{
                    ws.close();
                    addLogMessage('🔌 연결을 수동으로 종료했습니다.');
                }}
            }}
            
            function sendTestMessage() {{
                if (ws && ws.readyState === WebSocket.OPEN) {{
                    const message = {{
                        type: "test",
                        message: "AIRISS v4.0 테스트 메시지",
                        timestamp: new Date().toISOString()
                    }};
                    ws.send(JSON.stringify(message));
                    addLogMessage(`📤 전송: ${{JSON.stringify(message)}}`, 'sent');
                }} else {{
                    addLogMessage('❌ WebSocket이 연결되지 않았습니다.', 'error');
                }}
            }}
            
            function clearLog() {{
                document.getElementById('messageLog').innerHTML = 
                    '<div class="message-entry">🧹 로그가 초기화되었습니다.</div>';
            }}
            
            // 자동 연결 시도
            setTimeout(connectWebSocket, 1000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 메인 실행
if __name__ == "__main__":
    logger.info("🚀 Starting AIRISS v4.0 Standalone...")
    
    try:
        uvicorn.run(
            app,
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info",
            reload=False
        )
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        print("\n" + "="*60)
        print("🔧 문제 해결 방법:")
        print("1. 포트 8002가 사용 중인지 확인")
        print("2. 방화벽 설정 확인") 
        print("3. 필요 패키지: pip install fastapi uvicorn")
        print("="*60)
