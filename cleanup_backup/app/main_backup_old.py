# app/main.py
# AIRISS v4.0 메인 서버 - 라우터 등록 문제 완전 해결 버전
# 🔥 핵심 수정: startup 이벤트 제거, lifespan에서 proper async 처리

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
import asyncio

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

# 🔥 글로벌 서비스 인스턴스들 (lifespan에서 초기화)
sqlite_service = None
hybrid_analyzer = None

# 🔥 완전히 수정된 Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sqlite_service, hybrid_analyzer
    
    # 🚀 Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.0 Server Starting")
    logger.info(f"📡 HTTP: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📡 WebSocket: ws://{WS_HOST}:{SERVER_PORT}/ws/{{client_id}}")
    logger.info(f"🧪 Test WebSocket: ws://{WS_HOST}:{SERVER_PORT}/test-ws")
    logger.info(f"📊 Real-time Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info(f"📖 API Documentation: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 80)
    
    # 🔥 SQLiteService 초기화 (proper async 처리)
    try:
        logger.info("🗄️ SQLiteService 초기화 시작...")
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        
        # 🔥 핵심 수정: await로 proper async 호출
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 및 테이블 생성 완료")
        
        # 데이터베이스 상태 확인
        stats = await sqlite_service.get_database_stats()
        logger.info(f"📊 DB 상태: {stats}")
        
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        # 🔥 중요: 서비스는 계속 진행 (SQLite 없이도 기본 기능 동작)
        sqlite_service = None
    
    # 🔥 Analysis Engine 초기화 (안전한 방식)
    try:
        logger.info("🧠 AIRISS v4.0 하이브리드 분석기 초기화 시작...")
        from app.api.analysis import hybrid_analyzer as ha
        hybrid_analyzer = ha
        logger.info("✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ AIRISS v4.0 하이브리드 분석기 초기화 실패: {e}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        hybrid_analyzer = None
    
    # 🔥 등록된 라우트 확인 (startup 이후)
    await log_registered_routes(app)
    
    yield
    
    # 🛑 Shutdown
    logger.info("🛑 AIRISS v4.0 Server Shutting Down")
    
    # 리소스 정리
    if sqlite_service:
        try:
            # 필요시 연결 정리 로직 추가
            logger.info("🗄️ SQLite 연결 정리 완료")
        except Exception as e:
            logger.warning(f"SQLite 정리 중 오류: {e}")

# 🔥 라우트 로깅 함수 (async로 수정)
async def log_registered_routes(app: FastAPI):
    """등록된 모든 라우트 로깅"""
    logger.info("📋 등록된 모든 라우트:")
    total_routes = 0
    upload_found = False
    analysis_found = False
    
    for route in app.routes:
        if hasattr(route, 'path'):
            total_routes += 1
            
            # 라우트 정보 로깅
            if hasattr(route, 'methods') and route.methods:
                methods_str = ', '.join(route.methods)
                logger.info(f"  - [{methods_str}] {route.path}")
                
                # 특정 라우트 확인
                if '/upload' in route.path:
                    upload_found = True
                if '/analysis' in route.path:
                    analysis_found = True
            else:
                logger.info(f"  - [WebSocket] {route.path}")
    
    logger.info(f"📊 총 {total_routes}개 라우트가 등록되었습니다.")
    
    # 🔥 핵심 라우트 등록 상태 확인
    if upload_found:
        logger.info("✅ Upload 라우트가 성공적으로 등록되었습니다!")
    else:
        logger.warning("⚠️ Upload 라우트가 발견되지 않습니다!")
    
    if analysis_found:
        logger.info("✅ Analysis 라우트가 성공적으로 등록되었습니다!")
    else:
        logger.warning("⚠️ Analysis 라우트가 발견되지 않습니다!")

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
            "sqlite_database": sqlite_service is not None,
            "websocket_realtime": True,
            "airiss_analysis": hybrid_analyzer is not None,
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
            "connection_count": len(manager.active_connections),
            "sqlite_service": "active" if sqlite_service else "unavailable",
            "hybrid_analyzer": "active" if hybrid_analyzer else "unavailable"
        }
    }

@app.get("/health/db")
async def health_check_db():
    """데이터베이스 헬스체크"""
    if not sqlite_service:
        return {
            "status": "unavailable", 
            "error": "SQLiteService가 초기화되지 않았습니다",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # 기본 연결 테스트
        file_list = await sqlite_service.list_files()
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
    """분석 엔진 헬스체크"""
    if not hybrid_analyzer:
        return {
            "status": "unavailable",
            "error": "AIRISS 하이브리드 분석기가 초기화되지 않았습니다",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
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
        
    except Exception as e:
        logger.error(f"분석 엔진 헬스체크 오류: {e}")
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

# 📊 대시보드 페이지 (기존 코드 유지)
# app/main.py 의 대시보드 함수 교체용 코드
# 📊 대시보드 페이지 (Internal Server Error 해결 버전)

@app.get("/dashboard", response_class=HTMLResponse)
async def realtime_dashboard():
    """실시간 대시보드 페이지 - AIRISS v4.0 (오류 수정 버전)"""
    try:
        # 안전한 변수 할당
        server_port = SERVER_PORT if 'SERVER_PORT' in globals() else 8002
        ws_host = WS_HOST if 'WS_HOST' in globals() else "localhost"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v4.0 실시간 대시보드</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
        .system-info {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }}
        .success {{ color: #28a745; }}
        .error {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AIRISS v4.0</h1>
            <div class="subtitle">OK금융그룹 AI 기반 인재 분석 시스템</div>
            <div class="version-badge">착수보고서 완전 반영 버전</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2><span>🔌</span> WebSocket 연결</h2>
                <div id="connectionStatus" class="status disconnected">연결 대기 중...</div>
                <br><br>
                <button onclick="connectWebSocket()">연결 시작</button>
                <button onclick="disconnectWebSocket()">연결 해제</button>
                <button onclick="sendTestMessage()">테스트 메시지</button>
            </div>
            
            <div class="card">
                <h2><span>📊</span> 시스템 정보</h2>
                <div class="system-info">
                    <p><strong>서버 포트:</strong> {server_port}</p>
                    <p><strong>WebSocket:</strong> 실시간 지원</p>
                    <p><strong>데이터베이스:</strong> SQLite 통합</p>
                    <p><strong>분석 엔진:</strong> AIRISS v4.0</p>
                    <p><strong>8대 영역:</strong> 착수보고서 완전 반영</p>
                </div>
                <button onclick="window.open('/docs', '_blank')">📖 API 문서</button>
                <button onclick="window.open('/health', '_blank')">💊 헬스체크</button>
                <button onclick="testAPI()">🧪 API 테스트</button>
            </div>
            
            <div class="card">
                <h2><span>📝</span> 실시간 로그</h2>
                <div class="log-container" id="logContainer">
                    <div class="log-entry">
                        <span class="log-time">[시작]</span>
                        <span class="success">AIRISS v4.0 대시보드 로드 완료</span>
                    </div>
                    <div class="log-entry">
                        <span class="log-time">[정보]</span>
                        착수보고서 기준 8대 영역 적용됨
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2><span>🏆</span> AIRISS 8대 영역</h2>
                <div class="system-info">
                    <p><strong>1. 업무성과 (20%)</strong> - 업무 산출물의 양과 질</p>
                    <p><strong>2. KPI달성 (30%)</strong> - 핵심성과지표 달성도</p>
                    <p><strong>3. 태도마인드셋 (10%)</strong> - 일에 대한 태도</p>
                    <p><strong>4. 커뮤니케이션역량 (10%)</strong> - 의사소통 능력</p>
                    <p><strong>5. 리더십협업역량 (10%)</strong> - 리더십과 협업</p>
                    <p><strong>6. 지식전문성 (10%)</strong> - 전문성과 학습능력</p>
                    <p><strong>7. 라이프스타일건강 (5%)</strong> - 건강과 웰빙</p>
                    <p><strong>8. 윤리사외행동 (5%)</strong> - 윤리성과 평판</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let clientId = 'dashboard-' + Math.random().toString(36).substr(2, 9);
        
        function addLog(message, type = 'info') {{
            const logContainer = document.getElementById('logContainer');
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            
            let className = '';
            if (type === 'success') className = 'success';
            else if (type === 'error') className = 'error';
            else if (type === 'warning') className = 'warning';
            
            logEntry.innerHTML = `<span class="log-time">[` + timeStr + `]</span> <span class="` + className + `">` + message + `</span>`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
        }}
        
        function updateConnectionStatus(connected) {{
            const statusEl = document.getElementById('connectionStatus');
            if (connected) {{
                statusEl.className = 'status connected';
                statusEl.textContent = '✅ WebSocket 연결됨';
                addLog('WebSocket 연결 성공', 'success');
            }} else {{
                statusEl.className = 'status disconnected';
                statusEl.textContent = '❌ 연결 끊김';
                addLog('WebSocket 연결 해제', 'warning');
            }}
        }}
        
        function connectWebSocket() {{
            const wsUrl = `ws://{ws_host}:{server_port}/ws/` + clientId + `?channels=analysis,alerts`;
            addLog('WebSocket 연결 시도: ' + wsUrl);
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => updateConnectionStatus(true);
            
            ws.onmessage = (event) => {{
                try {{
                    const data = JSON.parse(event.data);
                    addLog('수신: ' + data.type + ' - ' + (data.message || JSON.stringify(data)));
                }} catch (e) {{
                    addLog('메시지 파싱 오류: ' + event.data, 'error');
                }}
            }};
            
            ws.onerror = (error) => {{
                addLog('WebSocket 오류: ' + error, 'error');
            }};
            
            ws.onclose = () => {{
                updateConnectionStatus(false);
            }};
        }}
        
        function disconnectWebSocket() {{
            if (ws) {{ 
                ws.close(); 
                addLog('WebSocket 연결 해제 요청', 'warning'); 
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
                addLog('테스트 메시지 전송', 'success');
            }} else {{
                addLog('WebSocket이 연결되지 않음', 'error');
            }}
        }}
        
        function testAPI() {{
            addLog('API 헬스체크 시작...');
            fetch('/health')
            .then(response => {{
                if (response.ok) {{
                    addLog('✅ API 서버 정상 작동!', 'success');
                    return response.json();
                }} else {{
                    addLog('❌ API 서버 오류: ' + response.status, 'error');
                    throw new Error('HTTP ' + response.status);
                }}
            }})
            .then(data => {{
                addLog('서버 상태: ' + data.status + ', 버전: ' + data.version, 'success');
            }})
            .catch(error => {{
                addLog('API 테스트 실패: ' + error.message, 'error');
            }});
        }}
        
        // 페이지 로드 시 자동 실행
        document.addEventListener('DOMContentLoaded', function() {{
            addLog('AIRISS v4.0 대시보드 초기화 완료', 'success');
            addLog('착수보고서 8대 영역 프레임워크 적용됨', 'success');
            
            // 자동 API 테스트
            setTimeout(testAPI, 1000);
        }});
    </script>
</body>
</html>
"""
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"대시보드 렌더링 오류: {e}")
        # 최소한의 안전한 HTML 반환
        error_html = f"""
<!DOCTYPE html>
<html>
<head><title>AIRISS v4.0 - 오류</title></head>
<body>
    <h1>🚀 AIRISS v4.0</h1>
    <p>대시보드 로딩 중 오류가 발생했습니다.</p>
    <p>오류: {str(e)}</p>
    <p><a href="/docs">API 문서로 이동</a></p>
    <p><a href="/health">헬스체크</a></p>
</body>
</html>
"""
        return HTMLResponse(content=error_html)

# 🔥 API 라우터 등록 (핵심 수정 부분)

logger.info("🔧 라우터 등록 프로세스 시작...")

# 🔥 Upload 라우터 등록 (에러 핸들링 강화)
try:
    logger.info("📁 Upload 라우터 import 시도...")
    from app.api.upload import router as upload_router
    logger.info("✅ Upload 라우터 import 성공")
    
    # 라우터 등록
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
    logger.error("💡 Upload 모듈을 찾을 수 없습니다. app/api/upload.py 파일을 확인해주세요.")
    
except Exception as e:
    logger.error(f"❌ Upload router registration error: {e}")
    logger.error(f"Registration traceback: {traceback.format_exc()}")

# 🔥 Analysis 라우터 등록 (에러 핸들링 강화)
try:
    logger.info("🧠 Analysis 라우터 import 시도...")
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
    logger.error("💡 Analysis 모듈을 찾을 수 없습니다. app/api/analysis.py 파일을 확인해주세요.")

except Exception as e:
    logger.error(f"❌ Analysis router registration failed: {e}")
    logger.error(f"Registration error details: {traceback.format_exc()}")
    logger.error("💡 Analysis 라우터 등록 중 오류가 발생했습니다.")

# 전체 라우터 등록 완료 로깅
logger.info("🏁 라우터 등록 프로세스 완료")

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