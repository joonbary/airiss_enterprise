# app/main.py
# AIRISS v4.0 메인 서버 - Analysis API 라우터 등록 문제 완전 해결 버전

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
import os
import uvicorn
from typing import Dict, List
from datetime import datetime
import traceback

# 프로젝트 모듈 import
from app.core.websocket_manager import ConnectionManager

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))
WS_HOST = os.getenv("WS_HOST", "localhost")

# WebSocket 연결 관리자 인스턴스 생성
manager = ConnectionManager()

# Startup 이벤트 처리 함수
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("📋 Registered routes:")
    route_count = 0
    
    for route in app.routes:
        if hasattr(route, 'path'):
            route_count += 1
            # WebSocket 라우트와 HTTP 라우트 구분
            if hasattr(route, 'methods'):
                # HTTP 라우트
                methods_str = ', '.join(route.methods) if route.methods else 'GET'
                logger.info(f"  - [{methods_str}] {route.path}")
            else:
                # WebSocket 라우트
                logger.info(f"  - [WebSocket] {route.path}")
    
    logger.info(f"📊 Total routes registered: {route_count}")

# Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.0 Server Starting")
    logger.info(f"📡 HTTP: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📡 WebSocket: ws://{WS_HOST}:{SERVER_PORT}/ws/{{client_id}}")
    logger.info(f"🧪 Test WebSocket: ws://{WS_HOST}:{SERVER_PORT}/test-ws")
    logger.info(f"📊 Real-time Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info(f"📖 API Documentation: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 80)
    
    # SQLiteService 초기화 (안전한 방식) - 🔥 데이터베이스 테이블 생성 추가
    try:
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        # 🔥 핵심 수정: 데이터베이스 테이블 초기화
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 및 테이블 생성 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    # Analysis Engine 초기화 (안전한 방식) - 🔥 AIRISS v4.0 수정
    try:
        from app.api.analysis import hybrid_analyzer
        logger.info("✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS v4.0 하이브리드 분석기 초기화 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
    
    # 시작 시 라우트 출력
    await startup_event()
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.0 Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0",
    description="AI-based Resource Intelligence Scoring System with Real-time WebSocket & SQLite Integration",
    version="4.0.0",
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

# 🎯 기본 엔드포인트들

@app.get("/")
async def root():
    """루트 엔드포인트 - API 정보 제공"""
    return {
        "message": "AIRISS v4.0 API Server",
        "version": "4.0.0",
        "status": "running",
        "description": "OK금융그룹 AI 기반 인재 분석 시스템",
        "features": {
            "sqlite_database": True,
            "websocket_realtime": True,
            "airiss_analysis": True,
            "hybrid_scoring": True,
            "modular_architecture": True
        },
        "endpoints": {
            "api_docs": f"http://{WS_HOST}:{SERVER_PORT}/docs",
            "dashboard": f"http://{WS_HOST}:{SERVER_PORT}/dashboard",
            "websocket_main": f"ws://{WS_HOST}:{SERVER_PORT}/ws/{{client_id}}",
            "websocket_test": f"ws://{WS_HOST}:{SERVER_PORT}/test-ws"
        },
        "connection_info": manager.get_connection_info(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """기본 헬스체크"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "service": "AIRISS v4.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "fastapi": "running",
            "websocket_manager": "active",
            "connection_count": len(manager.connections)
        }
    }

@app.get("/health/db")
async def health_check_db():
    """데이터베이스 헬스체크"""
    try:
        from app.db.sqlite_service import SQLiteService
        db_service = SQLiteService()
        
        # 기본 연결 테스트
        file_list = await db_service.list_files()
        file_count = len(file_list)
        
        return {
            "status": "healthy",
            "database": "SQLite",
            "files": file_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"DB 헬스체크 오류: {e}")
        return {
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/analysis")
async def health_check_analysis():
    """분석 엔진 헬스체크 - 🔥 AIRISS v4.0 수정 + 에러 핸들링 강화"""
    try:
        # 🔥 수정: analysis.py에서 직접 import + 에러 핸들링 강화
        logger.info("분석 엔진 헬스체크 시작")
        
        try:
            from app.api.analysis import hybrid_analyzer
            logger.info("하이브리드 분석기 import 성공")
            
            openai_available = getattr(
                getattr(hybrid_analyzer, 'text_analyzer', None), 
                'openai_available', 
                False
            )
            
            return {
                "status": "healthy",
                "analysis_engine": "AIRISS v4.0",
                "framework_dimensions": 8,
                "hybrid_analysis": True,
                "openai_available": openai_available,
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError as ie:
            logger.warning(f"분석 엔진 import 실패: {ie}")
            return {
                "status": "partial",
                "analysis_engine": "AIRISS v4.0",
                "framework_dimensions": 8,
                "hybrid_analysis": False,
                "openai_available": False,
                "warning": "Analysis engine import failed",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"분석 엔진 헬스체크 오류: {e}")
        logger.error(f"예외 상세: {traceback.format_exc()}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# 🔌 WebSocket 엔드포인트들

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    """메인 WebSocket 엔드포인트 - 채널 구독 지원"""
    logger.info(f"🔌 WebSocket connection attempt from: {client_id}")
    
    # 채널 파싱
    channel_list = channels.split(",") if channels else []
    
    try:
        # 연결 수락 및 채널 구독
        await manager.connect(websocket, client_id, channel_list)
        
        # 메시지 수신 대기
        while True:
            # 텍스트 메시지 수신
            message = await websocket.receive_text()
            
            # 메시지 처리
            await manager.handle_client_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

@app.websocket("/test-ws")
async def test_websocket(websocket: WebSocket):
    """간단한 테스트용 WebSocket - 에코 서버"""
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
            # 메시지 수신 및 에코
            data = await websocket.receive_text()
            logger.info(f"Test received: {data}")
            
            await websocket.send_json({
                "type": "echo",
                "original": data,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        logger.info("🧪 Test WebSocket disconnected")

# 📊 대시보드 페이지

@app.get("/dashboard", response_class=HTMLResponse)
async def realtime_dashboard():
    """실시간 대시보드 페이지 - AIRISS v4.0"""
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
                background: linear-gradient(135deg, #FF5722 0%, #F89C26 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
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
                color: #FF5722;
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            
            .subtitle {{
                color: #666;
                font-size: 1.2rem;
                margin-bottom: 20px;
            }}
            
            .version-badge {{
                display: inline-block;
                background: linear-gradient(135deg, #4A4A4A, #666);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
            }}
            
            .card {{
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
                margin-bottom: 20px;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
            }}
            
            .card h2 {{
                color: #FF5722;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 10px;
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
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                background: linear-gradient(135deg, #FF5722, #F89C26);
                color: white;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 5px;
                font-size: 1rem;
            }}
            
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 87, 34, 0.4);
            }}
            
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .endpoint-list {{
                list-style: none;
                padding: 0;
            }}
            
            .endpoint-list li {{
                padding: 10px 0;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .endpoint-list li:last-child {{
                border-bottom: none;
            }}
            
            .method {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: bold;
                color: white;
            }}
            
            .method.GET {{ background: #28a745; }}
            .method.POST {{ background: #007bff; }}
            .method.PUT {{ background: #ffc107; color: #333; }}
            .method.DELETE {{ background: #dc3545; }}
            .method.WS {{ background: #6f42c1; }}
            
            .log-container {{
                background: #2d3748;
                color: #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 0.9rem;
                max-height: 300px;
                overflow-y: auto;
            }}
            
            .log-entry {{
                margin-bottom: 5px;
                padding: 5px 0;
            }}
            
            .log-time {{
                color: #F89C26;
                margin-right: 10px;
            }}
            
            @media (max-width: 768px) {{
                .grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 AIRISS v4.0</h1>
                <div class="subtitle">OK금융그룹 AI 기반 인재 분석 시스템</div>
                <div class="version-badge">SQLite 통합 + 실시간 모니터링</div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2><span>🔌</span> WebSocket 연결</h2>
                    <div id="connectionStatus" class="status disconnected">
                        연결 대기 중...
                    </div>
                    <br><br>
                    <button onclick="connectWebSocket()">연결 시작</button>
                    <button onclick="disconnectWebSocket()">연결 해제</button>
                    <button onclick="sendTestMessage()">테스트 메시지</button>
                </div>
                
                <div class="card">
                    <h2><span>📊</span> 시스템 정보</h2>
                    <p><strong>서버 포트:</strong> {SERVER_PORT}</p>
                    <p><strong>WebSocket:</strong> 실시간 지원</p>
                    <p><strong>데이터베이스:</strong> SQLite 통합</p>
                    <p><strong>분석 엔진:</strong> AIRISS v4.0</p>
                    <br>
                    <button onclick="window.open('/docs', '_blank')">📖 API 문서</button>
                    <button onclick="window.open('/health', '_blank')">💊 헬스체크</button>
                </div>
                
                <div class="card">
                    <h2><span>🛠️</span> API 엔드포인트</h2>
                    <ul class="endpoint-list">
                        <li>
                            <span><span class="method GET">GET</span> /</span>
                            <span>API 정보</span>
                        </li>
                        <li>
                            <span><span class="method GET">GET</span> /health</span>
                            <span>헬스체크</span>
                        </li>
                        <li>
                            <span><span class="method POST">POST</span> /upload/upload/</span>
                            <span>파일 업로드</span>
                        </li>
                        <li>
                            <span><span class="method POST">POST</span> /analysis/start</span>
                            <span>분석 시작</span>
                        </li>
                        <li>
                            <span><span class="method GET">GET</span> /analysis/jobs</span>
                            <span>작업 목록</span>
                        </li>
                        <li>
                            <span><span class="method WS">WS</span> /ws/{{client_id}}</span>
                            <span>실시간 연결</span>
                        </li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2><span>📝</span> 실시간 로그</h2>
                    <div class="log-container" id="logContainer">
                        <div class="log-entry">
                            <span class="log-time">[시작]</span>
                            AIRISS v4.0 대시보드 로드 완료
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let clientId = 'dashboard-' + Math.random().toString(36).substr(2, 9);
            
            function addLog(message) {{
                const logContainer = document.getElementById('logContainer');
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                
                const now = new Date();
                const timeStr = now.toLocaleTimeString();
                
                logEntry.innerHTML = `<span class="log-time">[${timeStr}]</span> ${{message}}`;
                logContainer.appendChild(logEntry);
                logContainer.scrollTop = logContainer.scrollHeight;
            }}
            
            function updateConnectionStatus(connected) {{
                const statusEl = document.getElementById('connectionStatus');
                if (connected) {{
                    statusEl.className = 'status connected';
                    statusEl.textContent = '✅ WebSocket 연결됨';
                    addLog('WebSocket 연결 성공');
                }} else {{
                    statusEl.className = 'status disconnected';
                    statusEl.textContent = '❌ 연결 끊김';
                    addLog('WebSocket 연결 해제');
                }}
            }}
            
            function connectWebSocket() {{
                const wsUrl = `ws://{WS_HOST}:{SERVER_PORT}/ws/${{clientId}}?channels=analysis,alerts`;
                addLog(`WebSocket 연결 시도: ${{wsUrl}}`);
                
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {{
                    updateConnectionStatus(true);
                }};
                
                ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    addLog(`수신: ${{data.type}} - ${{data.message || JSON.stringify(data)}}`);
                }};
                
                ws.onerror = (error) => {{
                    addLog(`WebSocket 오류: ${{error}}`);
                }};
                
                ws.onclose = () => {{
                    updateConnectionStatus(false);
                }};
            }}
            
            function disconnectWebSocket() {{
                if (ws) {{
                    ws.close();
                    addLog('WebSocket 연결 해제 요청');
                }}
            }}
            
            function sendTestMessage() {{
                if (ws && ws.readyState === WebSocket.OPEN) {{
                    const message = {{
                        type: 'test',
                        message: 'AIRISS v4.0 테스트 메시지',
                        timestamp: new Date().toISOString()
                    }};
                    ws.send(JSON.stringify(message));
                    addLog('테스트 메시지 전송');
                }} else {{
                    addLog('WebSocket이 연결되지 않음');
                }}
            }}
            
            // 페이지 로드 시 자동 연결
            document.addEventListener('DOMContentLoaded', function() {{
                addLog('AIRISS v4.0 대시보드 초기화 완료');
                addLog('WebSocket 연결 준비 완료');
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 🔥 API 라우터 등록 (핵심 수정 부분)

logger.info("🔧 라우터 등록 프로세스 시작...")

# Upload 라우터 등록
try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ Upload router registered successfully")
    
    # Upload 라우트 확인
    upload_routes = []
    for route in upload_router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods_str = ', '.join(route.methods) if route.methods else 'UNKNOWN'
            upload_routes.append(f"{methods_str} {route.path}")
    
    logger.info(f"📊 Upload routes: {upload_routes}")
    
except ImportError as ie:
    logger.error(f"❌ Upload router import error: {ie}")
    logger.error(f"Import traceback: {traceback.format_exc()}")
except Exception as e:
    logger.error(f"❌ Upload router registration error: {e}")
    logger.error(f"Registration traceback: {traceback.format_exc()}")

# 🚀 Analysis 라우터 등록 (핵심 수정!)
try:
    logger.info("🔍 Analysis 라우터 import 시도...")
    from app.api.analysis import router as analysis_router
    logger.info("✅ Analysis 라우터 import 성공")
    
    # 라우터 등록
    app.include_router(analysis_router)
    logger.info("✅ Analysis router registered successfully")
    
    # Analysis 라우트 확인 및 로깅
    analysis_routes = []
    for route in analysis_router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods_str = ', '.join(route.methods) if route.methods else 'UNKNOWN'
            full_path = f"/analysis{route.path}" if not route.path.startswith('/analysis') else route.path
            analysis_routes.append(f"{methods_str} {full_path}")
    
    logger.info(f"📊 Analysis routes registered: {analysis_routes}")
    
    # 라우터 객체 정보 로깅
    logger.info(f"📋 Analysis router object: {type(analysis_router)}")
    logger.info(f"📋 Analysis router prefix: {getattr(analysis_router, 'prefix', 'No prefix')}")
    logger.info(f"📋 Analysis router tags: {getattr(analysis_router, 'tags', 'No tags')}")
    
except ImportError as ie:
    logger.error(f"❌ Analysis router import failed: {ie}")
    logger.error(f"Import error details: {traceback.format_exc()}")
    logger.error("💡 Analysis 모듈을 찾을 수 없습니다. app/api/analysis.py 파일을 생성해주세요.")

except Exception as e:
    logger.error(f"❌ Analysis router registration failed: {e}")
    logger.error(f"Registration error details: {traceback.format_exc()}")
    logger.error("💡 Analysis 라우터 등록 중 오류가 발생했습니다.")

# 전체 라우터 등록 완료 로깅
logger.info("🏁 라우터 등록 프로세스 완료")

# 등록된 모든 라우트 최종 확인
def log_all_routes():
    """등록된 모든 라우트 로깅"""
    logger.info("📋 최종 등록된 모든 라우트:")
    total_routes = 0
    
    for route in app.routes:
        if hasattr(route, 'path'):
            total_routes += 1
            if hasattr(route, 'methods') and route.methods:
                methods_str = ', '.join(route.methods)
                logger.info(f"  - [{methods_str}] {route.path}")
            else:
                logger.info(f"  - [WebSocket] {route.path}")
    
    logger.info(f"📊 총 {total_routes}개 라우트가 등록되었습니다.")
    
    # Analysis 라우트 특별 체크
    analysis_found = False
    for route in app.routes:
        if hasattr(route, 'path') and '/analysis' in route.path:
            analysis_found = True
            break
    
    if analysis_found:
        logger.info("✅ Analysis 라우트가 성공적으로 등록되었습니다!")
    else:
        logger.warning("⚠️ Analysis 라우트가 발견되지 않습니다!")

# 앱 시작 후 라우트 로깅
@app.on_event("startup")
async def startup_route_logging():
    """시작 시 라우트 로깅"""
    log_all_routes()

# 메인 실행
if __name__ == "__main__":
    logger.info("🚀 Starting AIRISS v4.0 directly...")
    logger.info(f"🌐 Server will start on: http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"📖 API docs will be available at: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info(f"📊 Dashboard will be available at: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    
    try:
        # reload를 False로 설정하여 직접 실행 시 안정성 확보
        uvicorn.run(
            "app.main:app",  # 모듈 경로로 지정
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info",
            reload=False,  # 직접 실행 시에는 reload 비활성화
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ 서버 시작 실패: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
        print(f"\n❌ 서버 시작 오류: {e}")
        print("\n📋 문제 해결 방법:")
        print("1. 포트 8002가 사용 중인지 확인: netstat -ano | findstr :8002")
        print("2. app/api/analysis.py 파일이 존재하는지 확인")
        print("3. SQLite 데이터베이스 파일 권한 확인")
        print("4. Python 가상환경이 활성화되어 있는지 확인")
        print("5. 필요한 패키지가 모두 설치되어 있는지 확인")
        input("\n엔터를 눌러 종료...")