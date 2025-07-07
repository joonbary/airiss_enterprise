# app/main_optimized.py
# AIRISS v4.0 최적화 버전 - 정적 파일 분리 + PWA 지원 + 성능 최적화

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
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
    level=logging.INFO,  # DEBUG에서 INFO로 변경하여 성능 향상
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 전역 설정
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))
WS_HOST = os.getenv("WS_HOST", "localhost")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# WebSocket 연결 관리자 인스턴스 생성
manager = ConnectionManager()

# 글로벌 서비스 인스턴스들
sqlite_service = None
hybrid_analyzer = None

# Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sqlite_service, hybrid_analyzer
    
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.0 Optimized Server Starting")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
    logger.info(f"📡 Main UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info(f"📖 API Documentation: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 80)
    
    # SQLiteService 초기화
    try:
        logger.info("🗄️ SQLiteService 초기화...")
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        sqlite_service = None
    
    # Analysis Engine 초기화
    try:
        logger.info("🧠 AIRISS 하이브리드 분석기 초기화...")
        from app.api.analysis import hybrid_analyzer as ha
        hybrid_analyzer = ha
        logger.info("✅ AIRISS 하이브리드 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS 하이브리드 분석기 초기화 실패: {e}")
        hybrid_analyzer = None
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.0 Optimized Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0 Optimized",
    description="AI-based Resource Intelligence Scoring System - Optimized for Production",
    version="4.0.2",
    lifespan=lifespan,
    docs_url="/docs" if ENVIRONMENT == "development" else None,  # Production에서 docs 숨김
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# CORS 설정 (Production 환경에서는 제한적 적용)
if ENVIRONMENT == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://airiss.okfinancial.com", "https://airiss-dev.okfinancial.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

# 정적 파일 서빙
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 템플릿 설정
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

templates = Jinja2Templates(directory=templates_dir)

# 🏠 최적화된 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def optimized_main_interface(request: Request):
    """AIRISS v4.0 최적화된 메인 인터페이스"""
    
    # 시스템 상태 확인
    system_status = {
        "database": "healthy" if sqlite_service else "unavailable",
        "analysis_engine": "healthy" if hybrid_analyzer else "unavailable",
        "environment": ENVIRONMENT,
        "version": "4.0.2",
        "features": {
            "pwa_enabled": True,
            "offline_support": True,
            "real_time_analysis": True,
            "mobile_optimized": True
        }
    }
    
    # 템플릿이 없는 경우 기본 HTML 반환
    template_path = os.path.join(templates_dir, "main.html")
    if not os.path.exists(template_path):
        return HTMLResponse(content=get_default_html(system_status))
    
    return templates.TemplateResponse("main.html", {
        "request": request,
        "system_status": system_status,
        "ws_host": WS_HOST,
        "server_port": SERVER_PORT,
        "environment": ENVIRONMENT
    })

def get_default_html(system_status):
    """기본 HTML 템플릿 (main.html이 없는 경우)"""
    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v4.0 Optimized</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <i class="fas fa-brain"></i>
                <div>
                    <h1>AIRISS v4.0 Optimized</h1>
                    <div class="subtitle">OK금융그룹 AI 기반 인재 분석 시스템</div>
                </div>
            </div>
            <div class="status-info">
                <div class="status-item">
                    <i class="fas fa-database"></i>
                    <span>데이터베이스:</span>
                    <span class="{'status-good' if system_status['database'] == 'healthy' else 'status-error'}">{system_status['database']}</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-cogs"></i>
                    <span>분석엔진:</span>
                    <span class="{'status-good' if system_status['analysis_engine'] == 'healthy' else 'status-error'}">{system_status['analysis_engine']}</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-users"></i>
                    <span>접속자:</span>
                    <span class="status-good" id="connectionCount">0</span>
                </div>
            </div>
        </div>
    </header>

    <div id="notification" class="notification">
        <div class="notification-content">
            <i id="notificationIcon" class="fas fa-check-circle"></i>
            <span id="notificationText"></span>
        </div>
    </div>

    <main class="container">
        <div class="main-grid">
            <section class="card">
                <h2><i class="fas fa-upload"></i> 파일 업로드 및 분석</h2>
                
                <div class="upload-area">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">Excel 또는 CSV 파일을 업로드하세요</div>
                    <div class="upload-hint">클릭하거나 파일을 여기로 드래그하세요</div>
                </div>
                
                <input type="file" id="fileInput" style="display: none;" accept=".xlsx,.xls,.csv">
                
                <div style="margin-top: 20px; text-align: center;">
                    <button class="button" id="analyzeBtn" disabled onclick="startAnalysis()">
                        <i class="fas fa-brain"></i> AI 분석 시작
                    </button>
                    <button class="button secondary" onclick="showSampleData()">
                        <i class="fas fa-file-download"></i> 샘플 데이터
                    </button>
                    <button class="button secondary" id="testApiBtn" onclick="testAnalysisAPI()">
                        <i class="fas fa-tools"></i> 시스템 테스트
                    </button>
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none;">
                    <div class="file-info-item">
                        <strong><i class="fas fa-file"></i> 파일명:</strong>
                        <span id="fileName"></span>
                    </div>
                    <div class="file-info-item">
                        <strong><i class="fas fa-weight"></i> 크기:</strong>
                        <span id="fileSize"></span>
                    </div>
                    <div class="file-info-item">
                        <strong><i class="fas fa-info-circle"></i> 상태:</strong>
                        <span id="fileStatus">업로드 완료</span>
                    </div>
                </div>
            </section>
            
            <section class="card">
                <h2><i class="fas fa-chart-line"></i> 분석 현황 및 결과</h2>
                
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span><i class="fas fa-tasks"></i> 분석 진행률:</span>
                        <span id="progressText">대기 중</span>
                    </div>
                    <div class="progress-container">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <button class="button" onclick="loadRecentJobs()">
                        <i class="fas fa-history"></i> 최근 분석 조회
                    </button>
                    {'<button class="button secondary" onclick="window.open(\'/docs\', \'_blank\')"><i class="fas fa-book"></i> API 문서</button>' if system_status['environment'] == 'development' else ''}
                </div>
                
                <div id="recentJobs"></div>
            </section>
        </div>
        
        <section class="features-grid">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-target"></i></div>
                <div class="feature-title">업무성과 & KPI (50%)</div>
                <div class="feature-desc">업무 산출물의 양과 질, 핵심성과지표 달성도를 종합 분석</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-comments"></i></div>
                <div class="feature-title">태도 & 커뮤니케이션 (20%)</div>
                <div class="feature-desc">업무에 대한 마인드셋과 동료 간 의사소통 효과성을 AI 기반으로 정량 평가</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-users-cog"></i></div>
                <div class="feature-title">리더십 & 협업 (20%)</div>
                <div class="feature-desc">리더십 발휘 능력과 팀 협업 기여도, 전문성 향상 의지를 다면적으로 측정</div>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-balance-scale"></i></div>
                <div class="feature-title">건강 & 윤리 (10%)</div>
                <div class="feature-desc">라이프-워크 밸런스와 윤리성, 평판 관리 수준을 종합적으로 검증</div>
            </div>
        </section>
    </main>

    <script src="/static/js/main.js"></script>
    <script>
        window.AIRISS_CONFIG = {{
            version: '{system_status['version']}',
            environment: '{system_status['environment']}',
            wsHost: '{WS_HOST}',
            wsPort: {SERVER_PORT},
            features: {system_status['features']},
            systemStatus: {system_status}
        }};
    </script>
</body>
</html>
"""

# 🌐 API 엔드포인트들
@app.get("/api/status")
async def api_status():
    """시스템 상태 API"""
    return {
        "service": "AIRISS v4.0 Optimized",
        "version": "4.0.2",
        "status": "healthy",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "healthy" if sqlite_service else "unavailable",
            "analysis_engine": "healthy" if hybrid_analyzer else "unavailable",
            "websocket": "active",
            "connections": len(manager.active_connections)
        },
        "features": {
            "pwa_enabled": True,
            "offline_support": True,
            "real_time_sync": True,
            "mobile_optimized": True,
            "production_ready": ENVIRONMENT == "production"
        }
    }

@app.get("/health")
async def health_check():
    """상세 헬스체크"""
    health_status = "healthy"
    components = {}
    
    # 데이터베이스 상태
    try:
        if sqlite_service:
            file_count = len(await sqlite_service.list_files())
            components["database"] = {"status": "healthy", "files": file_count}
        else:
            components["database"] = {"status": "unavailable", "error": "Not initialized"}
            health_status = "degraded"
    except Exception as e:
        components["database"] = {"status": "error", "error": str(e)}
        health_status = "unhealthy"
    
    # 분석 엔진 상태
    try:
        if hybrid_analyzer:
            components["analysis_engine"] = {"status": "healthy", "dimensions": 8}
        else:
            components["analysis_engine"] = {"status": "unavailable", "error": "Not initialized"}
            health_status = "degraded"
    except Exception as e:
        components["analysis_engine"] = {"status": "error", "error": str(e)}
        health_status = "unhealthy"
    
    # WebSocket 상태
    components["websocket"] = {
        "status": "healthy",
        "active_connections": len(manager.active_connections)
    }
    
    return {
        "status": health_status,
        "version": "4.0.2",
        "timestamp": datetime.now().isoformat(),
        "components": components
    }

@app.get("/health/db")
async def health_check_db():
    """데이터베이스 헬스체크"""
    if not sqlite_service:
        return {"status": "unavailable", "error": "SQLiteService가 초기화되지 않았습니다", "timestamp": datetime.now().isoformat()}
    
    try:
        file_list = await sqlite_service.list_files()
        return {"status": "healthy", "database": "SQLite", "files": len(file_list), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/health/analysis")
async def health_check_analysis():
    """분석 엔진 헬스체크"""
    if not hybrid_analyzer:
        return {"status": "unavailable", "error": "AIRISS 하이브리드 분석기가 초기화되지 않았습니다", "timestamp": datetime.now().isoformat()}
    
    try:
        openai_available = getattr(getattr(hybrid_analyzer, 'text_analyzer', None), 'openai_available', False)
        
        return {
            "status": "healthy",
            "analysis_engine": "AIRISS v4.0 Optimized",
            "framework_dimensions": 8,
            "hybrid_analysis": True,
            "openai_available": openai_available,
            "enhanced_features": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# 🔌 WebSocket 엔드포인트
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    """최적화된 WebSocket 엔드포인트"""
    logger.info(f"🔌 Optimized WebSocket connection: {client_id}")
    channel_list = channels.split(",") if channels else []
    
    try:
        await manager.connect(websocket, client_id, channel_list)
        
        # 연결 환영 메시지
        await websocket.send_json({
            "type": "welcome",
            "message": "AIRISS v4.0 Optimized에 연결되었습니다",
            "version": "4.0.2",
            "features": ["real_time_analysis", "offline_sync", "pwa_support"],
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            message = await websocket.receive_text()
            await manager.handle_client_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Optimized WebSocket {client_id} disconnected")
    except Exception as e:
        logger.error(f"Optimized WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# 🔧 개발자 도구 (개발 환경에서만)
if ENVIRONMENT == "development":
    @app.get("/dashboard", response_class=HTMLResponse)
    async def developer_dashboard():
        """개발자 대시보드"""
        return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>AIRISS v4.0 Optimized 개발자 대시보드</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .card {{ background: white; padding: 20px; margin: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #FF5722; }}
            .status {{ padding: 5px 10px; border-radius: 20px; color: white; }}
            .healthy {{ background: #4CAF50; }}
            .warning {{ background: #FF9800; }}
            .error {{ background: #f44336; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔧 AIRISS v4.0 Optimized - 개발자 대시보드</h1>
            <p><strong>메인 UI:</strong> <a href="/" target="_blank">http://{WS_HOST}:{SERVER_PORT}/</a></p>
            <p><strong>API 문서:</strong> <a href="/docs" target="_blank">http://{WS_HOST}:{SERVER_PORT}/docs</a></p>
            <p><strong>환경:</strong> <span class="status healthy">{ENVIRONMENT}</span></p>
            <p><strong>버전:</strong> 4.0.2 (Optimized)</p>
            <p><strong>최적화:</strong> ✅ 정적 파일 분리, PWA 지원</p>
        </div>
    </body>
    </html>
    """)

# 라우터 등록
logger.info("🔧 최적화된 라우터 등록...")

try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router, prefix="/upload", tags=["파일 업로드"])
    logger.info("✅ Upload router registered")
except Exception as e:
    logger.error(f"❌ Upload router error: {e}")

try:
    from app.api.analysis import router as analysis_router
    app.include_router(analysis_router, prefix="/analysis", tags=["AI 분석"])
    logger.info("✅ Analysis router registered")
except Exception as e:
    logger.error(f"❌ Analysis router error: {e}")

# 메인 실행
if __name__ == "__main__":
    logger.info("🚀 Starting AIRISS v4.0 Optimized Server...")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
    logger.info(f"🏠 Main UI: http://{WS_HOST}:{SERVER_PORT}/")
    
    if ENVIRONMENT == "development":
        logger.info(f"📖 API docs: http://{WS_HOST}:{SERVER_PORT}/docs")
        logger.info(f"🔧 Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    
    try:
        uvicorn.run(
            "app.main_optimized:app",
            host=SERVER_HOST,
            port=SERVER_PORT,
            log_level="info",
            reload=(ENVIRONMENT == "development"),
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ 최적화된 서버 시작 실패: {e}")
        logger.error(f"오류 상세: {traceback.format_exc()}")
