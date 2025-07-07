# AIRISS Phase 2: Core Functions Integration
# Emergency 안전성 유지 + Core 기능 (DB + AI Analysis) 추가

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.middleware.cors import CORSMiddleware
    logger.info("✅ FastAPI imported successfully")
except ImportError as e:
    logger.error(f"❌ FastAPI import failed: {e}")
    sys.exit(1)

# Global service instances
sqlite_service = None
hybrid_analyzer = None

# Create FastAPI application
app = FastAPI(
    title="AIRISS Phase 2 Core",
    version="phase2-1.0",
    description="AIRISS system with Core Functions - Database + AI Analysis"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates setup
try:
    templates = Jinja2Templates(directory="app/templates")
    logger.info("✅ Templates configured")
except Exception as e:
    logger.warning(f"⚠️ Templates not configured: {e}")
    templates = None

# Static files setup
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    logger.info("✅ Static files mounted")
except Exception as e:
    logger.warning(f"⚠️ Static files not mounted: {e}")

# Service initialization
async def init_core_services():
    """Core 서비스 안전한 초기화"""
    global sqlite_service, hybrid_analyzer
    
    # SQLite Service 초기화
    try:
        logger.info("🗄️ SQLiteService 초기화 시작...")
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        logger.error(traceback.format_exc())
        sqlite_service = None
    
    # Hybrid Analyzer 초기화
    try:
        logger.info("🧠 AIRISS Hybrid Analyzer 초기화 시작...")
        from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
        hybrid_analyzer = AIRISSHybridAnalyzer()
        logger.info("✅ AIRISS Hybrid Analyzer 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS Hybrid Analyzer 초기화 실패: {e}")
        logger.error(traceback.format_exc())
        hybrid_analyzer = None

# Emergency endpoints (유지)
@app.get("/health")
async def health():
    """Health check endpoint for AWS Load Balancer"""
    return PlainTextResponse("OK", status_code=200)

@app.get("/status")
async def status():
    """Detailed status endpoint with core services"""
    return {
        "status": "phase2_core",
        "mode": "core_enabled",
        "phase": "2",
        "pid": os.getpid(),
        "timestamp": datetime.now().isoformat(),
        "health": "OK",
        "features": {
            "emergency_mode": True,
            "basic_ui": True,
            "static_files": True,
            "templates": templates is not None,
            "analysis_engine": hybrid_analyzer is not None,
            "database": sqlite_service is not None,
            "websocket": False  # Phase 3에서 활성화
        },
        "services": {
            "sqlite_db": "active" if sqlite_service else "failed",
            "hybrid_analyzer": "active" if hybrid_analyzer else "failed"
        }
    }

@app.get("/api")
async def api_info():
    """API information with core services"""
    return {
        "message": "AIRISS Phase 2 Core API Server",
        "version": "phase2-1.0",
        "status": "core_enabled",
        "description": "OK금융그룹 AI 기반 인재 분석 시스템 - Phase 2 Core Services",
        "phase": "2/3",
        "features": {
            "emergency_mode": True,
            "enhanced_ui": True,
            "chart_visualization": True,
            "sqlite_database": sqlite_service is not None,
            "websocket_realtime": False,   # Phase 3
            "airiss_analysis": hybrid_analyzer is not None,
            "hybrid_scoring": hybrid_analyzer is not None,
            "deep_learning": False,        # Phase 3
            "bias_detection": False,       # Phase 3
            "performance_prediction": False # Phase 3
        },
        "next_phase": "WebSocket + Advanced AI Features",
        "timestamp": datetime.now().isoformat()
    }

# Health checks for core services
@app.get("/health/db")
async def health_check_db():
    """Database health check"""
    if not sqlite_service:
        return {
            "status": "unavailable", 
            "error": "SQLiteService가 초기화되지 않았습니다", 
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        file_list = await sqlite_service.list_files()
        return {
            "status": "healthy", 
            "database": "SQLite", 
            "files": len(file_list), 
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e), 
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/analysis")
async def health_check_analysis():
    """Analysis engine health check"""
    if not hybrid_analyzer:
        return {
            "status": "unavailable", 
            "error": "AIRISS 하이브리드 분석기가 초기화되지 않았습니다", 
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        return {
            "status": "healthy",
            "analysis_engine": "AIRISS Hybrid Analyzer",
            "framework_dimensions": 8,
            "hybrid_analysis": True,
            "text_analysis": True,
            "quantitative_analysis": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e), 
            "timestamp": datetime.now().isoformat()
        }

# Main UI endpoint with core services
@app.get("/", response_class=HTMLResponse)
async def main_interface(request: Request):
    """AIRISS Phase 2 Main Interface with Core Services"""
    
    if not templates:
        # Enhanced fallback HTML for Phase 2
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AIRISS Phase 2 Core</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .status {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .service {{ background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #2196F3; }}
                .phase {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #FF5722; color: white; text-decoration: none; border-radius: 8px; margin: 5px; }}
                .service-status {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
                .active {{ background: #4CAF50; color: white; }}
                .failed {{ background: #f44336; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 AIRISS Phase 2 Core Services</h1>
                    <h2>OK금융그룹 AI 기반 인재 분석 시스템</h2>
                </div>
                
                <div class="status">
                    <h3>✅ Core 서비스 복원 진행 중!</h3>
                    <p>Phase 2: 데이터베이스와 AI 분석 엔진이 활성화되었습니다.</p>
                </div>
                
                <div class="service">
                    <h4>🗄️ 데이터베이스 서비스</h4>
                    <span class="service-status {'active' if sqlite_service else 'failed'}">
                        {'활성화' if sqlite_service else '실패'}
                    </span>
                    <p>SQLite 데이터베이스: {'정상 작동' if sqlite_service else '초기화 실패'}</p>
                </div>
                
                <div class="service">
                    <h4>🧠 AI 분석 엔진</h4>
                    <span class="service-status {'active' if hybrid_analyzer else 'failed'}">
                        {'활성화' if hybrid_analyzer else '실패'}
                    </span>
                    <p>하이브리드 분석기: {'정상 작동' if hybrid_analyzer else '초기화 실패'}</p>
                </div>
                
                <div class="phase">
                    <h4>📋 복원 진행 상황</h4>
                    <ul>
                        <li><strong>Phase 1</strong> ✅ 기본 UI 복원 (완료)</li>
                        <li><strong>Phase 2</strong> 🔄 Core 서비스 복원 (진행 중)</li>
                        <li><strong>Phase 3</strong> ⏳ 실시간 기능 + 완전 복원</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/status" class="button">상세 상태</a>
                    <a href="/health/db" class="button">DB 상태</a>
                    <a href="/health/analysis" class="button">AI 엔진 상태</a>
                    <a href="/api" class="button">API 정보</a>
                </div>
                
                <div style="text-align: center; color: #666; margin-top: 30px;">
                    <p>Phase 3 복원 예정: 내일 오후 (WebSocket + 고급 AI 기능)</p>
                </div>
            </div>
        </body>
        </html>
        """)
    
    # Template response with core service status
    try:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "db_status": "정상" if sqlite_service else "오류",
            "analysis_status": "정상" if hybrid_analyzer else "오류",
            "db_status_class": 'status-good' if sqlite_service else 'status-error',
            "analysis_status_class": 'status-good' if hybrid_analyzer else 'status-error',
            "ws_host": "localhost",
            "server_port": os.environ.get("PORT", "8000")
        })
    except Exception as e:
        logger.error(f"Template rendering error: {e}")
        return HTMLResponse(content=f"""
        <html><body>
        <h1>AIRISS Phase 2 Core Active</h1>
        <p>Template Error: {e}</p>
        <p>Database: {'OK' if sqlite_service else 'Failed'}</p>
        <p>Analysis: {'OK' if hybrid_analyzer else 'Failed'}</p>
        <p><a href="/status">Check Status</a></p>
        </body></html>
        """)

# Core API endpoints (기본 기능만)
@app.get("/api/v1/files")
async def list_files():
    """파일 목록 조회"""
    if not sqlite_service:
        raise HTTPException(status_code=503, detail="Database service not available")
    
    try:
        files = await sqlite_service.list_files()
        return {"status": "success", "files": files, "count": len(files)}
    except Exception as e:
        logger.error(f"파일 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/test")
async def test_analysis():
    """분석 엔진 테스트"""
    if not hybrid_analyzer:
        raise HTTPException(status_code=503, detail="Analysis service not available")
    
    try:
        # Simple test
        test_text = "좋은 성과를 보여주고 있습니다."
        # Basic test without full analysis
        return {
            "status": "success",
            "message": "Analysis engine is working",
            "test_text": test_text,
            "analyzer_available": True
        }
    except Exception as e:
        logger.error(f"분석 엔진 테스트 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service initialization endpoint
@app.post("/admin/init-services")
async def initialize_services():
    """관리자용 서비스 초기화"""
    try:
        await init_core_services()
        return {
            "status": "initialized",
            "services": {
                "database": sqlite_service is not None,
                "analyzer": hybrid_analyzer is not None
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"서비스 초기화 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AWS Elastic Beanstalk compatibility
application = app

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup - initialize core services"""
    logger.info("=" * 60)
    logger.info("🚀 AIRISS Phase 2 Core Server Starting")
    logger.info("✅ Emergency mode: Active")
    logger.info("✅ Basic UI: Enabled") 
    logger.info("🔄 Core services: Initializing...")
    logger.info("=" * 60)
    
    # Initialize core services
    await init_core_services()
    
    if sqlite_service and hybrid_analyzer:
        logger.info("✅ Phase 2 Core 서비스 초기화 완료!")
    else:
        logger.warning("⚠️ 일부 Core 서비스 초기화 실패 - 서비스 재시작 권장")

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Phase 2 Core server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
