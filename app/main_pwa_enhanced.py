# app/main_pwa_enhanced.py
# AIRISS v4.0 PWA Enhanced - 모바일 앱처럼 사용 가능한 고급 UI/UX

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

# 글로벌 서비스 인스턴스들
sqlite_service = None
hybrid_analyzer = None

# Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sqlite_service, hybrid_analyzer
    
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.0 PWA Enhanced - 모바일 앱화 완료")
    logger.info(f"📱 PWA URL: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Advanced UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"🔧 Developer API: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info(f"📋 Service Worker: http://{WS_HOST}:{SERVER_PORT}/static/pwa/sw.js")
    logger.info("=" * 80)
    
    # 서비스 초기화
    try:
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        sqlite_service = None
    
    try:
        from app.api.analysis import hybrid_analyzer as ha
        hybrid_analyzer = ha
        logger.info("✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS v4.0 하이브리드 분석기 초기화 실패: {e}")
        hybrid_analyzer = None
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.0 PWA Enhanced Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.0 PWA Enhanced",
    description="AI-based Resource Intelligence Scoring System - Progressive Web App Edition",
    version="4.0.2",
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

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# PWA 매니페스트 제공
@app.get("/manifest.json")
async def get_manifest():
    """PWA 매니페스트 파일 제공"""
    return FileResponse("app/static/pwa/manifest.json", media_type="application/json")

# Service Worker 제공
@app.get("/sw.js")
async def get_service_worker():
    """Service Worker 파일 제공"""
    return FileResponse("app/static/pwa/sw.js", media_type="application/javascript")

# 🏠 PWA Enhanced 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def pwa_enhanced_interface():
    """AIRISS v4.0 PWA Enhanced - 모바일 앱처럼 사용 가능한 고급 인터페이스"""
    
    # 시스템 상태 확인
    db_status = "정상" if sqlite_service else "오류"
    analysis_status = "정상" if hybrid_analyzer else "오류"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#FF5722">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="AIRISS v4.0">
    
    <title>AIRISS v4.0 PWA - OK금융그룹 AI 인재분석</title>
    <meta name="description" content="OK금융그룹 AI 기반 직원 성과/역량 스코어링 시스템 - 모바일 앱처럼 사용하세요">
    
    <!-- PWA 매니페스트 -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- 파비콘 -->
    <link rel="icon" type="image/png" sizes="192x192" href="/static/pwa/icon-192.png">
    <link rel="apple-touch-icon" href="/static/pwa/icon-192.png">
    
    <!-- 외부 라이브러리 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {{
            --primary-color: #FF5722;
            --secondary-color: #F89C26;
            --success-color: #4CAF50;
            --warning-color: #FF9800;
            --danger-color: #f44336;
            --dark-color: #1a1a1a;
            --light-bg: #f8f9fa;
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            --border-radius: 15px;
            --safe-area-inset-top: env(safe-area-inset-top);
            --safe-area-inset-bottom: env(safe-area-inset-bottom);
            --safe-area-inset-left: env(safe-area-inset-left);
            --safe-area-inset-right: env(safe-area-inset-right);
        }}
        
        /* 기본 스타일 초기화 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }}
        
        html {{
            height: 100%;
            overflow-x: hidden;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            min-height: -webkit-fill-available;
            color: #333;
            overflow-x: hidden;
            position: relative;
            
            /* iOS Safe Area 지원 */
            padding-top: var(--safe-area-inset-top);
            padding-bottom: var(--safe-area-inset-bottom);
            padding-left: var(--safe-area-inset-left);
            padding-right: var(--safe-area-inset-right);
        }}
        
        /* PWA 설치 배너 */
        .install-banner {{
            position: fixed;
            top: var(--safe-area-inset-top, 0);
            left: 0;
            right: 0;
            background: linear-gradient(135deg, var(--dark-color), #2c2c2c);
            color: white;
            padding: 15px 20px;
            z-index: 10000;
            transform: translateY(-100%);
            transition: transform 0.3s ease;
            text-align: center;
        }}
        
        .install-banner.show {{
            transform: translateY(0);
        }}
        
        .install-banner button {{
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            margin-left: 15px;
            cursor: pointer;
            font-weight: bold;
        }}
        
        .install-banner .close-btn {{
            background: transparent;
            border: 1px solid #ccc;
            color: #ccc;
            padding: 4px 8px;
            margin-left: 10px;
        }}
        
        /* 향상된 헤더 */
        .header {{
            background: linear-gradient(135deg, var(--dark-color), #2c2c2c);
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: sticky;
            top: var(--safe-area-inset-top, 0);
            z-index: 1000;
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .logo {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .logo i {{
            font-size: 2.5rem;
            color: var(--primary-color);
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        .logo-text h1 {{
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .logo-text .subtitle {{
            font-size: 0.9rem;
            color: #ccc;
            margin-top: 2px;
        }}
        
        .pwa-badge {{
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ box-shadow: 0 0 10px rgba(255, 87, 34, 0.5); }}
            to {{ box-shadow: 0 0 20px rgba(255, 87, 34, 0.8), 0 0 30px rgba(255, 87, 34, 0.6); }}
        }}
        
        .status-info {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.85rem;
        }}
        
        .status-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}
        
        .status-item:hover {{
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }}
        
        .status-good {{ color: var(--success-color); }}
        .status-error {{ color: var(--danger-color); }}
        
        /* 컨테이너 */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 15px;
        }}
        
        /* 퀵 액션 버튼들 */
        .quick-actions {{
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .quick-action {{
            background: rgba(255, 255, 255, 0.95);
            border: none;
            border-radius: 12px;
            padding: 15px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: bold;
            color: var(--dark-color);
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .quick-action:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .quick-action i {{
            font-size: 1.2rem;
            color: var(--primary-color);
        }}
        
        /* 메인 그리드 */
        .main-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        /* 향상된 카드 */
        .card {{
            background: rgba(255, 255, 255, 0.98);
            border-radius: var(--border-radius);
            padding: 25px;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }}
        
        .card h2 {{
            color: var(--primary-color);
            font-size: 1.4rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card h2 i {{
            font-size: 1.3rem;
        }}
        
        /* 향상된 업로드 영역 */
        .upload-area {{
            border: 3px dashed var(--primary-color);
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            background: linear-gradient(135deg, #fafafa, #f5f5f5);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .upload-area:hover {{
            border-color: var(--secondary-color);
            background: linear-gradient(135deg, #f0f0f0, #e8e8e8);
            transform: scale(1.02);
        }}
        
        .upload-area.dragover {{
            border-color: var(--success-color);
            background: linear-gradient(135deg, #e8f5e8, #d4f4d4);
            transform: scale(1.05);
        }}
        
        .upload-icon {{
            font-size: 3rem;
            margin-bottom: 15px;
            color: var(--primary-color);
            animation: bounce 2s infinite;
        }}
        
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        
        .upload-text {{
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .upload-hint {{
            font-size: 0.9rem;
            color: #999;
            margin: 5px 0;
        }}
        
        /* 향상된 버튼 */
        .button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1rem;
            margin: 5px;
            position: relative;
            overflow: hidden;
            touch-action: manipulation;
            user-select: none;
        }}
        
        .button:active {{
            transform: scale(0.95);
        }}
        
        .button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(255, 87, 34, 0.4);
        }}
        
        .button:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        
        .button.secondary {{
            background: linear-gradient(135deg, #6c757d, #5a6268);
        }}
        
        .button.loading {{
            color: transparent;
        }}
        
        .button.loading::after {{
            content: "";
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: button-loading-spinner 1s ease infinite;
        }}
        
        @keyframes button-loading-spinner {{
            from {{ transform: rotate(0turn); }}
            to {{ transform: rotate(1turn); }}
        }}
        
        /* 향상된 진행률 바 */
        .progress-container {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 16px;
            overflow: hidden;
            margin: 15px 0;
            position: relative;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .progress-fill::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: progressShine 2s infinite;
        }}
        
        @keyframes progressShine {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .progress-text {{
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
            color: var(--dark-color);
        }}
        
        /* 알림 시스템 */
        .notification {{
            position: fixed;
            top: calc(var(--safe-area-inset-top, 0px) + 20px);
            right: 20px;
            background: white;
            border-left: 5px solid var(--success-color);
            border-radius: 12px;
            padding: 15px 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            z-index: 9999;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            min-width: 320px;
            max-width: 90vw;
        }}
        
        .notification.show {{
            transform: translateX(0);
        }}
        
        .notification.error {{ border-color: var(--danger-color); }}
        .notification.warning {{ border-color: var(--warning-color); }}
        .notification.info {{ border-color: var(--primary-color); }}
        
        /* 오프라인 인디케이터 */
        .offline-indicator {{
            position: fixed;
            bottom: var(--safe-area-inset-bottom, 20px);
            left: 50%;
            transform: translateX(-50%);
            background: var(--danger-color);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .offline-indicator.show {{
            opacity: 1;
        }}
        
        /* 차트 컨테이너 */
        .chart-container {{
            background: white;
            border-radius: var(--border-radius);
            padding: 25px;
            margin-top: 30px;
            box-shadow: var(--card-shadow);
            position: relative;
            min-height: 400px;
        }}
        
        .chart-container.hidden {{
            display: none;
        }}
        
        /* 결과 카드 그리드 */
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .result-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-top: 4px solid var(--primary-color);
        }}
        
        .result-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }}
        
        .result-score {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 10px;
        }}
        
        .result-label {{
            color: #666;
            font-size: 1rem;
            font-weight: 500;
        }}
        
        /* 모바일 최적화 */
        @media (max-width: 768px) {{
            .container {{
                padding: 20px 10px;
            }}
            
            .header-content {{
                flex-direction: column;
                text-align: center;
            }}
            
            .status-info {{
                justify-content: center;
            }}
            
            .main-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .card {{
                padding: 20px;
            }}
            
            .upload-area {{
                padding: 25px 15px;
                min-height: 180px;
            }}
            
            .quick-actions {{
                gap: 10px;
            }}
            
            .quick-action {{
                padding: 12px 16px;
                font-size: 0.9rem;
            }}
            
            .button {{
                padding: 10px 20px;
                font-size: 0.9rem;
            }}
            
            .notification {{
                right: 10px;
                min-width: 280px;
            }}
        }}
        
        /* 초소형 모바일 */
        @media (max-width: 480px) {{
            .container {{
                padding: 15px 8px;
            }}
            
            .card {{
                padding: 15px;
            }}
            
            .upload-area {{
                padding: 20px 10px;
                min-height: 160px;
            }}
            
            .upload-icon {{
                font-size: 2.5rem;
            }}
            
            .upload-text {{
                font-size: 1rem;
            }}
            
            .button {{
                padding: 8px 16px;
                font-size: 0.85rem;
            }}
        }}
        
        /* 다크모드 지원 */
        @media (prefers-color-scheme: dark) {{
            .card {{
                background: rgba(30, 30, 30, 0.95);
                color: #e0e0e0;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .upload-area {{
                background: linear-gradient(135deg, #2a2a2a, #1f1f1f);
                border-color: var(--primary-color);
            }}
            
            .upload-text, .upload-hint {{
                color: #ccc;
            }}
        }}
        
        /* 접근성 개선 */
        @media (prefers-reduced-motion: reduce) {{
            *, ::before, ::after {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        
        /* 고대비 모드 */
        @media (prefers-contrast: high) {{
            .card {{
                border: 2px solid #000;
            }}
            
            .button {{
                border: 2px solid #000;
            }}
        }}
    </style>
</head>
<body>
    <!-- PWA 설치 배너 -->
    <div class="install-banner" id="installBanner">
        <span>📱 AIRISS를 홈 화면에 추가하여 앱처럼 사용하세요!</span>
        <button onclick="installPWA()" id="installButton">설치하기</button>
        <button class="close-btn" onclick="hideInstallBanner()">×</button>
    </div>

    <!-- 오프라인 인디케이터 -->
    <div class="offline-indicator" id="offlineIndicator">
        <i class="fas fa-wifi"></i> 오프라인 모드
    </div>

    <!-- 알림 -->
    <div id="notification" class="notification">
        <div style="display: flex; align-items: center; gap: 10px;">
            <i id="notificationIcon" class="fas fa-check-circle"></i>
            <span id="notificationText"></span>
        </div>
    </div>

    <!-- 헤더 -->
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <i class="fas fa-brain"></i>
                <div class="logo-text">
                    <h1>AIRISS v4.0</h1>
                    <div class="subtitle">OK금융그룹 AI 인재분석 시스템</div>
                </div>
                <div class="pwa-badge">PWA Ready</div>
            </div>
            <div class="status-info">
                <div class="status-item">
                    <i class="fas fa-database"></i>
                    <span>DB:</span>
                    <span class="{'status-good' if db_status == '정상' else 'status-error'}">{db_status}</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-cogs"></i>
                    <span>AI:</span>
                    <span class="{'status-good' if analysis_status == '정상' else 'status-error'}">{analysis_status}</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-users"></i>
                    <span>접속자:</span>
                    <span class="status-good" id="connectionCount">0</span>
                </div>
                <div class="status-item" id="networkStatus">
                    <i class="fas fa-wifi"></i>
                    <span>온라인</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- 퀵 액션 버튼들 -->
        <div class="quick-actions">
            <button class="quick-action" onclick="document.getElementById('fileInput').click()">
                <i class="fas fa-upload"></i> 빠른 업로드
            </button>
            <button class="quick-action" onclick="showResultsChart()">
                <i class="fas fa-chart-radar"></i> 결과 보기
            </button>
            <button class="quick-action" onclick="testAnalysisAPI()">
                <i class="fas fa-tools"></i> 시스템 점검
            </button>
            <a class="quick-action" href="/docs" target="_blank">
                <i class="fas fa-book"></i> API 문서
            </a>
        </div>

        <div class="main-grid">
            <!-- 파일 업로드 카드 -->
            <div class="card animate__animated animate__fadeInLeft">
                <h2><i class="fas fa-cloud-upload-alt"></i> 스마트 파일 분석</h2>
                
                <div class="upload-area" onclick="document.getElementById('fileInput').click()" 
                     ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                    <div class="upload-icon">
                        <i class="fas fa-file-excel"></i>
                    </div>
                    <div class="upload-text">Excel/CSV 파일을 드롭하세요</div>
                    <div class="upload-hint">📊 8대 영역 AI 분석 지원</div>
                    <div class="upload-hint">💾 최대 10MB까지 업로드 가능</div>
                </div>
                
                <input type="file" id="fileInput" style="display: none;" accept=".xlsx,.xls,.csv" onchange="handleFileSelect(event)">
                
                <div style="margin-top: 20px; text-align: center;">
                    <button class="button" onclick="startAnalysis()" id="analyzeBtn" disabled>
                        <i class="fas fa-brain"></i> AI 분석 시작
                    </button>
                    <button class="button secondary" onclick="showSampleData()">
                        <i class="fas fa-download"></i> 샘플 데이터
                    </button>
                </div>
                
                <div id="fileInfo" class="file-info" style="display: none; margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid var(--primary-color);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <strong><i class="fas fa-file"></i> 파일:</strong>
                        <span id="fileName"></span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <strong><i class="fas fa-weight"></i> 크기:</strong>
                        <span id="fileSize"></span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <strong><i class="fas fa-check-circle"></i> 상태:</strong>
                        <span id="fileStatus">업로드 완료</span>
                    </div>
                </div>
            </div>
            
            <!-- 실시간 분석 현황 카드 -->
            <div class="card animate__animated animate__fadeInRight">
                <h2><i class="fas fa-chart-line"></i> 실시간 분석 현황</h2>
                
                <div style="margin-bottom: 20px;">
                    <div class="progress-text" id="progressText">분석 대기 중 📊</div>
                    <div class="progress-container">
                        <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <button class="button" onclick="loadRecentJobs()">
                        <i class="fas fa-history"></i> 최근 분석
                    </button>
                    <button class="button secondary" onclick="shareResults()">
                        <i class="fas fa-share-alt"></i> 결과 공유
                    </button>
                </div>
                
                <div id="recentJobs" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- 차트 컨테이너 -->
        <div class="chart-container hidden" id="chartContainer">
            <h3 style="text-align: center; margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas fa-chart-radar"></i> AIRISS 8대 영역 분석 결과
            </h3>
            <canvas id="resultsChart"></canvas>
        </div>
        
        <!-- 결과 카드 그리드 -->
        <div class="results-grid" id="resultsGrid" style="display: none;">
            <!-- JavaScript로 동적 생성 -->
        </div>
    </div>

    <script>
        // 전역 변수
        let selectedFile = null;
        let currentJobId = null;
        let ws = null;
        let resultsChart = null;
        let deferredPrompt = null;
        let isOnline = navigator.onLine;
        
        // PWA 관련 기능들
        
        // Service Worker 등록
        if ('serviceWorker' in navigator) {{
            window.addEventListener('load', () => {{
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {{
                        console.log('✅ Service Worker 등록 성공:', registration.scope);
                        showNotification('오프라인 모드가 활성화되었습니다! 📱', 'info');
                    }})
                    .catch(error => {{
                        console.log('❌ Service Worker 등록 실패:', error);
                    }});
            }});
        }}
        
        // PWA 설치 이벤트 처리
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            
            // 설치 배너 표시
            const installBanner = document.getElementById('installBanner');
            const hasInstalledBefore = localStorage.getItem('pwa_install_dismissed');
            
            if (!hasInstalledBefore) {{
                installBanner.classList.add('show');
            }}
        }});
        
        function installPWA() {{
            const installButton = document.getElementById('installButton');
            
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                installButton.textContent = '설치 중...';
                installButton.disabled = true;
                
                deferredPrompt.userChoice.then((choiceResult) => {{
                    if (choiceResult.outcome === 'accepted') {{
                        showNotification('AIRISS PWA가 설치되었습니다! 홈 화면에서 확인하세요 🎉', 'success');
                        hideInstallBanner();
                    }} else {{
                        showNotification('설치가 취소되었습니다. 나중에 다시 시도하실 수 있습니다.', 'info');
                    }}
                    deferredPrompt = null;
                    installButton.textContent = '설치하기';
                    installButton.disabled = false;
                }});
            }} else {{
                showNotification('브라우저에서 홈 화면에 추가 옵션을 사용해주세요 📱', 'info');
            }}
        }}
        
        function hideInstallBanner() {{
            document.getElementById('installBanner').classList.remove('show');
            localStorage.setItem('pwa_install_dismissed', 'true');
        }}
        
        // 네트워크 상태 모니터링
        function updateNetworkStatus() {{
            const networkStatus = document.getElementById('networkStatus');
            const offlineIndicator = document.getElementById('offlineIndicator');
            
            if (navigator.onLine) {{
                networkStatus.innerHTML = '<i class="fas fa-wifi"></i> <span>온라인</span>';
                networkStatus.className = 'status-item';
                offlineIndicator.classList.remove('show');
                isOnline = true;
                
                if (!isOnline) {{
                    showNotification('인터넷 연결이 복구되었습니다! 🌐', 'success');
                }}
            }} else {{
                networkStatus.innerHTML = '<i class="fas fa-wifi-slash"></i> <span>오프라인</span>';
                networkStatus.className = 'status-item status-error';
                offlineIndicator.classList.add('show');
                isOnline = false;
                
                showNotification('오프라인 모드입니다. 일부 기능을 사용할 수 있습니다 📱', 'warning');
            }}
        }}
        
        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        
        // 알림 시스템
        function showNotification(message, type = 'success') {{
            const notification = document.getElementById('notification');
            const text = document.getElementById('notificationText');
            const icon = document.getElementById('notificationIcon');
            
            const iconMap = {{
                'success': 'fas fa-check-circle',
                'error': 'fas fa-times-circle',
                'warning': 'fas fa-exclamation-triangle',
                'info': 'fas fa-info-circle'
            }};
            
            text.textContent = message;
            icon.className = iconMap[type] || iconMap.success;
            notification.className = 'notification ' + type + ' show';
            
            // 진동 피드백 (모바일)
            if ('vibrate' in navigator) {{
                navigator.vibrate(type === 'error' ? [200, 100, 200] : [100]);
            }}
            
            setTimeout(() => {{
                notification.classList.remove('show');
            }}, 5000);
        }}
        
        // WebSocket 연결
        function connectWebSocket() {{
            if (!isOnline) {{
                console.log('오프라인 상태로 WebSocket 연결 생략');
                return;
            }}
            
            const clientId = 'pwa-enhanced-' + Math.random().toString(36).substr(2, 9);
            
            try {{
                ws = new WebSocket(`ws://{WS_HOST}:{SERVER_PORT}/ws/${{clientId}}?channels=analysis,alerts`);
                
                ws.onopen = () => {{
                    console.log('WebSocket 연결 성공');
                    updateConnectionCount();
                }};
                
                ws.onmessage = (event) => {{
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                }};
                
                ws.onclose = () => {{
                    console.log('WebSocket 연결 해제');
                    if (isOnline) {{
                        setTimeout(connectWebSocket, 3000); // 재연결 시도
                    }}
                }};
                
                ws.onerror = (error) => {{
                    console.error('WebSocket 오류:', error);
                }};
            }} catch (error) {{
                console.error('WebSocket 연결 실패:', error);
            }}
        }}
        
        function handleWebSocketMessage(data) {{
            if (data.type === 'analysis_progress' && data.job_id === currentJobId) {{
                updateProgress(data.progress, data.processed, data.total);
            }} else if (data.type === 'analysis_completed' && data.job_id === currentJobId) {{
                updateProgress(100, data.total_processed, data.total_processed);
                showNotification(`분석 완료! 평균 점수: ${{data.average_score}}점 🎉`, 'success');
                setTimeout(() => {{
                    loadRecentJobs();
                    showResultsChart();
                }}, 1000);
            }} else if (data.type === 'analysis_failed' && data.job_id === currentJobId) {{
                showNotification('분석 중 오류 발생: ' + data.error, 'error');
                resetAnalysisButton();
            }}
        }}
        
        function updateConnectionCount() {{
            if (!isOnline) return;
            
            fetch('/health')
            .then(response => response.json())
            .then(data => {{
                const count = data.components?.connection_count || '0';
                document.getElementById('connectionCount').textContent = count;
            }})
            .catch(() => {{
                document.getElementById('connectionCount').textContent = '?';
            }});
        }}
        
        // 파일 처리
        function handleDragOver(e) {{
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        }}
        
        function handleDragLeave(e) {{
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
        }}
        
        function handleDrop(e) {{
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {{
                handleFile(files[0]);
            }}
        }}
        
        function handleFileSelect(e) {{
            const file = e.target.files[0];
            if (file) {{
                handleFile(file);
            }}
        }}
        
        function handleFile(file) {{
            // 파일 유효성 검사
            if (file.size > 10 * 1024 * 1024) {{
                showNotification('파일 크기가 10MB를 초과합니다 📂', 'error');
                return;
            }}
            
            const allowedTypes = ['.xlsx', '.xls', '.csv'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(fileExtension)) {{
                showNotification('Excel 또는 CSV 파일만 지원합니다 📊', 'error');
                return;
            }}
            
            selectedFile = file;
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('analyzeBtn').disabled = false;
            
            showNotification('파일이 선택되었습니다! ✨', 'success');
            uploadFile(file);
        }}
        
        function formatFileSize(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }}
        
        function uploadFile(file) {{
            if (!isOnline) {{
                showNotification('오프라인 상태에서는 파일 업로드가 불가능합니다 📱', 'warning');
                return;
            }}
            
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('fileStatus').textContent = '업로드 중...';
            
            fetch('/upload/upload/', {{
                method: 'POST',
                body: formData
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(data => {{
                if (data.id) {{
                    selectedFile.fileId = data.id;
                    document.getElementById('fileStatus').textContent = 
                        `업로드 완료 (${{data.total_records || '?'}}건)`;
                    showNotification('파일 업로드 성공! 🎯', 'success');
                }} else {{
                    throw new Error('파일 ID를 받지 못했습니다');
                }}
            }})
            .catch(error => {{
                document.getElementById('fileStatus').textContent = '업로드 실패';
                showNotification('업로드 오류: ' + error.message, 'error');
            }});
        }}
        
        // 분석 시작
        function startAnalysis() {{
            if (!isOnline) {{
                showNotification('오프라인 상태에서는 분석을 시작할 수 없습니다 📱', 'warning');
                return;
            }}
            
            if (!selectedFile || !selectedFile.fileId) {{
                showNotification('먼저 파일을 업로드해주세요 📤', 'error');
                return;
            }}
            
            const analysisData = {{
                file_id: selectedFile.fileId,
                sample_size: 10,
                analysis_mode: 'hybrid',
                enable_ai_feedback: false
            }};
            
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = true;
            analyzeBtn.classList.add('loading');
            document.getElementById('progressText').textContent = '분석 시작 중... 🚀';
            
            fetch('/analysis/start', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify(analysisData)
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error(`HTTP ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(data => {{
                if (data.job_id) {{
                    currentJobId = data.job_id;
                    showNotification('AI 분석이 시작되었습니다! 📊', 'success');
                    updateProgress(0, 0, analysisData.sample_size);
                }} else {{
                    throw new Error('Job ID를 받지 못했습니다');
                }}
            }})
            .catch(error => {{
                showNotification('분석 시작 오류: ' + error.message, 'error');
                resetAnalysisButton();
            }});
        }}
        
        function resetAnalysisButton() {{
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('loading');
            document.getElementById('progressText').textContent = '분석 대기 중 📊';
        }}
        
        function updateProgress(percent, processed, total) {{
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = 
                `진행률: ${{percent.toFixed(1)}}% (${{processed}}/${{total}}) 🔄`;
        }}
        
        // 차트 표시
        function showResultsChart() {{
            const chartContainer = document.getElementById('chartContainer');
            chartContainer.classList.remove('hidden');
            
            if (resultsChart) {{
                resultsChart.destroy();
            }}
            
            const sampleData = {{
                labels: ['업무성과', 'KPI달성', '태도', '커뮤니케이션', '리더십', '협업', '전문성', '윤리'],
                datasets: [{{
                    label: '평균 점수',
                    data: [85, 78, 92, 76, 88, 94, 82, 90],
                    backgroundColor: 'rgba(255, 87, 34, 0.2)',
                    borderColor: 'rgba(255, 87, 34, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(255, 87, 34, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }}]
            }};
            
            const ctx = document.getElementById('resultsChart').getContext('2d');
            resultsChart = new Chart(ctx, {{
                type: 'radar',
                data: sampleData,
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{
                            beginAtZero: true,
                            max: 100,
                            grid: {{
                                color: 'rgba(255, 87, 34, 0.2)'
                            }},
                            pointLabels: {{
                                font: {{
                                    size: 12,
                                    weight: 'bold'
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
            
            createResultCards();
        }}
        
        function createResultCards() {{
            const resultsGrid = document.getElementById('resultsGrid');
            const labels = ['업무성과', 'KPI달성', '태도', '커뮤니케이션', '리더십', '협업', '전문성', '윤리'];
            const data = [85, 78, 92, 76, 88, 94, 82, 90];
            
            let cardsHTML = '';
            labels.forEach((label, index) => {{
                const score = data[index];
                const color = score >= 90 ? '#4CAF50' : score >= 80 ? '#FF9800' : '#FF5722';
                
                cardsHTML += `
                    <div class="result-card animate__animated animate__fadeInUp" style="animation-delay: ${{index * 0.1}}s;">
                        <div class="result-score" style="color: ${{color}}">${{score}}</div>
                        <div class="result-label">${{label}}</div>
                    </div>
                `;
            }});
            
            resultsGrid.innerHTML = cardsHTML;
            resultsGrid.style.display = 'grid';
        }}
        
        // 최근 작업 로드
        function loadRecentJobs() {{
            if (!isOnline) {{
                document.getElementById('recentJobs').innerHTML = 
                    '<p style="text-align: center; color: #666;">오프라인 상태에서는 최근 작업을 불러올 수 없습니다 📱</p>';
                return;
            }}
            
            fetch('/analysis/jobs')
            .then(response => response.json())
            .then(jobs => {{
                displayJobs(jobs);
            }})
            .catch(error => {{
                document.getElementById('recentJobs').innerHTML = 
                    '<p style="text-align: center; color: var(--danger-color);">작업 목록을 불러올 수 없습니다 ⚠️</p>';
            }});
        }}
        
        function displayJobs(jobs) {{
            const container = document.getElementById('recentJobs');
            
            if (jobs.length === 0) {{
                container.innerHTML = `
                    <div style="text-align: center; padding: 30px; color: #666;">
                        <i class="fas fa-inbox" style="font-size: 2.5rem; margin-bottom: 15px; color: #ccc;"></i>
                        <p>아직 분석 작업이 없습니다</p>
                        <p style="font-size: 0.9rem; margin-top: 10px;">파일을 업로드하여 첫 분석을 시작해보세요! 🚀</p>
                    </div>
                `;
                return;
            }}
            
            let html = '<h4 style="margin-bottom: 15px; color: var(--primary-color);"><i class="fas fa-history"></i> 최근 분석</h4>';
            
            jobs.slice(0, 3).forEach((job, index) => {{
                const createdDate = new Date(job.created_at || Date.now()).toLocaleString();
                const statusIcon = job.status === 'completed' ? 'fas fa-check-circle' : 
                                 job.status === 'failed' ? 'fas fa-times-circle' : 'fas fa-clock';
                const statusColor = job.status === 'completed' ? 'var(--success-color)' : 
                                  job.status === 'failed' ? 'var(--danger-color)' : 'var(--warning-color)';
                
                html += `
                    <div style="padding: 12px; border-left: 4px solid var(--primary-color); background: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: bold; margin-bottom: 4px;">
                                    <i class="fas fa-file-excel" style="color: var(--primary-color); margin-right: 8px;"></i>
                                    ${{job.filename || 'Unknown File'}}
                                </div>
                                <div style="font-size: 0.85rem; color: #666;">
                                    <i class="${{statusIcon}}" style="color: ${{statusColor}}; margin-right: 5px;"></i>
                                    ${{job.processed || 0}}명 분석 • ${{createdDate}}
                                </div>
                            </div>
                            <button class="button" onclick="viewResults('${{job.job_id}}')" 
                                    style="padding: 6px 12px; font-size: 0.8rem;">
                                <i class="fas fa-chart-bar"></i> 보기
                            </button>
                        </div>
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        function viewResults(jobId) {{
            showNotification('결과 페이지로 이동합니다 📊', 'info');
            window.open('/docs', '_blank');
        }}
        
        // 시스템 테스트
        function testAnalysisAPI() {{
            if (!isOnline) {{
                showNotification('오프라인 상태에서는 시스템 테스트를 할 수 없습니다 📱', 'warning');
                return;
            }}
            
            showNotification('시스템 점검을 시작합니다... 🔧', 'info');
            
            Promise.all([
                fetch('/health').then(r => r.json()),
                fetch('/health/db').then(r => r.json()),
                fetch('/health/analysis').then(r => r.json())
            ])
            .then(([health, db, analysis]) => {{
                const allHealthy = health.status === 'healthy' && 
                                 db.status === 'healthy' && 
                                 analysis.status === 'healthy';
                
                if (allHealthy) {{
                    showNotification('모든 시스템이 정상 작동 중입니다! ✅', 'success');
                }} else {{
                    showNotification('일부 시스템에 문제가 있습니다 ⚠️', 'warning');
                }}
            }})
            .catch(() => {{
                showNotification('시스템 점검 중 오류가 발생했습니다 ❌', 'error');
            }});
        }}
        
        // 결과 공유
        function shareResults() {{
            if (navigator.share) {{
                navigator.share({{
                    title: 'AIRISS v4.0 분석 결과',
                    text: 'OK금융그룹 AI 기반 인재 분석 시스템으로 분석한 결과를 확인해보세요!',
                    url: window.location.href
                }})
                .then(() => showNotification('공유가 완료되었습니다! 📤', 'success'))
                .catch(() => showNotification('공유를 취소했습니다', 'info'));
            }} else {{
                // 폴백: 클립보드에 복사
                navigator.clipboard.writeText(window.location.href)
                .then(() => showNotification('링크가 클립보드에 복사되었습니다! 📋', 'success'))
                .catch(() => showNotification('공유 기능을 사용할 수 없습니다', 'error'));
            }}
        }}
        
        // 샘플 데이터
        function showSampleData() {{
            const sampleData = `UID,이름,의견,성과등급,KPI점수
EMP001,김철수,매우 열심히 업무에 임하고 동료들과 원활한 소통을 하고 있습니다.,A,85
EMP002,이영희,창의적인 아이디어로 프로젝트를 성공적으로 이끌었습니다.,B+,78
EMP003,박민수,시간 관리와 업무 효율성 측면에서 개선이 필요합니다.,C,65`;
            
            const blob = new Blob([sampleData], {{ type: 'text/csv;charset=utf-8;' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AIRISS_샘플데이터.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('샘플 데이터가 다운로드되었습니다! 📥', 'success');
        }}
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🚀 AIRISS v4.0 PWA Enhanced 초기화');
            
            // 네트워크 상태 확인
            updateNetworkStatus();
            
            // WebSocket 연결 (온라인인 경우만)
            if (isOnline) {{
                connectWebSocket();
                updateConnectionCount();
                loadRecentJobs();
                
                // 정기 업데이트
                setInterval(() => {{
                    if (isOnline) {{
                        updateConnectionCount();
                    }}
                }}, 30000);
            }}
            
            showNotification('AIRISS v4.0 PWA가 시작되었습니다! 📱✨', 'info');
        }});
        
        // 페이지 언로드 시 정리
        window.addEventListener('beforeunload', function() {{
            if (ws) {{
                ws.close();
            }}
        }});
        
        // 키보드 단축키
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.key === 'u') {{
                e.preventDefault();
                document.getElementById('fileInput').click();
            }}
        }});
    </script>
</body>
</html>
"""
    
    return HTMLResponse(content=html_content)

# 기존 엔드포인트들 유지
@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "message": "AIRISS v4.0 PWA Enhanced",
        "version": "4.0.2",
        "status": "running",
        "description": "OK금융그룹 AI 기반 인재 분석 시스템 - PWA Edition",
        "features": {
            "pwa_ready": True,
            "offline_support": True,
            "mobile_optimized": True,
            "push_notifications": True,
            "chart_visualization": True,
            "sqlite_database": sqlite_service is not None,
            "websocket_realtime": True,
            "airiss_analysis": hybrid_analyzer is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# 기존 헬스체크 엔드포인트들
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "4.0.2",
        "service": "AIRISS v4.0 PWA Enhanced",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "fastapi": "running",
            "websocket_manager": "active", 
            "connection_count": len(manager.active_connections),
            "sqlite_service": "active" if sqlite_service else "unavailable",
            "hybrid_analyzer": "active" if hybrid_analyzer else "unavailable",
            "pwa_features": "active"
        }
    }

@app.get("/health/db")
async def health_check_db():
    if not sqlite_service:
        return {"status": "unavailable", "error": "SQLiteService 미초기화", "timestamp": datetime.now().isoformat()}
    
    try:
        file_list = await sqlite_service.list_files()
        return {"status": "healthy", "database": "SQLite", "files": len(file_list), "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/health/analysis")
async def health_check_analysis():
    if not hybrid_analyzer:
        return {"status": "unavailable", "error": "분석기 미초기화", "timestamp": datetime.now().isoformat()}
    
    try:
        return {
            "status": "healthy",
            "analysis_engine": "AIRISS v4.0 PWA Enhanced",
            "framework_dimensions": 8,
            "hybrid_analysis": True,
            "pwa_ready": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# WebSocket 엔드포인트
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    logger.info(f"🔌 PWA WebSocket connection: {client_id}")
    channel_list = channels.split(",") if channels else []
    
    try:
        await manager.connect(websocket, client_id, channel_list)
        while True:
            message = await websocket.receive_text()
            await manager.handle_client_message(client_id, message)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"PWA WebSocket error: {e}")
        manager.disconnect(client_id)

# 라우터 등록
try:
    from app.api.upload import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ Upload router registered")
except Exception as e:
    logger.error(f"❌ Upload router error: {e}")

try:
    from app.api.analysis import router as analysis_router
    app.include_router(analysis_router)
    logger.info("✅ Analysis router registered")
except Exception as e:
    logger.error(f"❌ Analysis router error: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting AIRISS v4.0 PWA Enhanced Server...")
    
    try:
        uvicorn.run(
            "app.main_pwa_enhanced:app",
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info",
            reload=False
        )
    except Exception as e:
        logger.error(f"❌ PWA Enhanced 서버 시작 실패: {e}")
