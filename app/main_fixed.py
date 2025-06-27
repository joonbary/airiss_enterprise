# app/main_fixed.py
# AIRISS v4.1 향상된 UI/UX 버전 - CSS 충돌 문제 해결

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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

# 글로벌 서비스 인스턴스들 (lifespan에서 초기화)
sqlite_service = None
hybrid_analyzer = None

# Lifespan 컨텍스트 매니저
@asynccontextmanager
async def lifespan(app: FastAPI):
    global sqlite_service, hybrid_analyzer
    
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 AIRISS v4.1 Enhanced UI/UX Server Starting")
    logger.info(f"📡 HTTP: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"🏠 Enhanced UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Dashboard: http://{WS_HOST}:{SERVER_PORT}/dashboard")
    logger.info(f"📖 API Documentation: http://{WS_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 80)
    
    # SQLiteService 초기화
    try:
        logger.info("🗄️ SQLiteService 초기화 시작...")
        from app.db.sqlite_service import SQLiteService
        sqlite_service = SQLiteService()
        await sqlite_service.init_database()
        logger.info("✅ SQLiteService 초기화 완료")
    except Exception as e:
        logger.error(f"❌ SQLiteService 초기화 실패: {e}")
        sqlite_service = None
    
    # Analysis Engine 초기화
    try:
        logger.info("🧠 AIRISS v4.1 하이브리드 분석기 초기화 시작...")
        from app.api.analysis import hybrid_analyzer as ha
        hybrid_analyzer = ha
        logger.info("✅ AIRISS v4.1 하이브리드 분석기 초기화 완료")
    except Exception as e:
        logger.error(f"❌ AIRISS v4.1 하이브리드 분석기 초기화 실패: {e}")
        hybrid_analyzer = None
    
    yield
    
    # Shutdown
    logger.info("🛑 AIRISS v4.1 Enhanced Server Shutting Down")

# FastAPI 앱 생성
app = FastAPI(
    title="AIRISS v4.1 Enhanced",
    description="AI-based Resource Intelligence Scoring System - Enhanced UI/UX Edition with Deep Learning",
    version="4.1.0",
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

# HTML 템플릿 - CSS 중괄호 문제 해결
def get_main_html(db_status: str, analysis_status: str) -> str:
    """메인 HTML 템플릿 반환 - 문자열 연결 방식으로 변경"""
    
    # 상태에 따른 클래스 설정
    db_class = 'status-good' if db_status == '정상' else 'status-error'
    analysis_class = 'status-good' if analysis_status == '정상' else 'status-error'
    
    # HTML 템플릿을 부분별로 구성
    html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRISS v4.1 Enhanced - OK금융그룹 AI 기반 인재 분석 시스템</title>
    
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Animate.css for smooth animations -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>"""
    
    # CSS 부분은 그대로 유지
    html_template += """
        :root {
            --primary-color: #FF5722;
            --secondary-color: #F89C26;
            --success-color: #4CAF50;
            --warning-color: #FF9800;
            --danger-color: #f44336;
            --dark-color: #1a1a1a;
            --light-bg: #f8f9fa;
            --card-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            --border-radius: 15px;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            min-height: 100vh;
            color: #333;
            overflow-x: hidden;
        }
        
        /* 헤더 스타일 */
        .header {
            background: linear-gradient(135deg, var(--dark-color), #2c2c2c);
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo i {
            font-size: 2rem;
            color: var(--primary-color);
        }
        
        .logo h1 {
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo .subtitle {
            font-size: 0.9rem;
            color: #ccc;
            margin-top: 2px;
        }
        
        .status-info {
            display: flex;
            gap: 20px;
            font-size: 0.85rem;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            transition: all 0.3s ease;
        }
        
        .status-item:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .status-good { color: var(--success-color); }
        .status-error { color: var(--danger-color); }
        
        /* 메인 컨테이너 */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        /* 온보딩 투어 */
        .onboarding-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            display: none;
            justify-content: center;
            align-items: center;
        }
        
        .onboarding-modal {
            background: white;
            border-radius: var(--border-radius);
            padding: 40px;
            max-width: 600px;
            text-align: center;
            animation: fadeInScale 0.5s ease;
        }
        
        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        
        /* 알림 시스템 */
        .notification {
            position: fixed;
            top: 100px;
            right: 20px;
            background: white;
            border-left: 5px solid var(--success-color);
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: var(--card-shadow);
            z-index: 9999;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            min-width: 300px;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.error { border-color: var(--danger-color); }
        .notification.warning { border-color: var(--warning-color); }
        
        /* 메인 그리드 */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }
        
        /* 카드 스타일 */
        .card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: var(--border-radius);
            padding: 30px;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
        }
        
        .card h2 {
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 i {
            font-size: 1.3rem;
        }
        
        /* 업로드 영역 */
        .upload-area {
            border: 3px dashed var(--primary-color);
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            background: linear-gradient(135deg, #fafafa, #f5f5f5);
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .upload-area::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .upload-area:hover {
            border-color: var(--secondary-color);
            background: linear-gradient(135deg, #f0f0f0, #e8e8e8);
            transform: scale(1.02);
        }
        
        .upload-area:hover::before {
            left: 100%;
        }
        
        .upload-area.dragover {
            border-color: var(--success-color);
            background: linear-gradient(135deg, #e8f5e8, #d4f4d4);
            transform: scale(1.05);
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: var(--primary-color);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .upload-text {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .upload-hint {
            font-size: 0.9rem;
            color: #999;
            margin-bottom: 5px;
        }
        
        /* 버튼 스타일 */
        .button {
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
        }
        
        .button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(255, 87, 34, 0.4);
        }
        
        .button:hover::before {
            left: 100%;
        }
        
        .button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .button.secondary {
            background: linear-gradient(135deg, #6c757d, #5a6268);
        }
        
        .button.secondary:hover {
            box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4);
        }
        
        .button.loading {
            position: relative;
            color: transparent;
        }
        
        .button.loading::after {
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
        }
        
        @keyframes button-loading-spinner {
            from { transform: rotate(0turn); }
            to { transform: rotate(1turn); }
        }
        
        /* 진행률 바 */
        .progress-container {
            background: #e0e0e0;
            border-radius: 10px;
            height: 12px;
            overflow: hidden;
            margin: 15px 0;
            position: relative;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: progressShine 2s infinite;
        }
        
        @keyframes progressShine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            background: white;
            border-radius: var(--border-radius);
            padding: 25px;
            margin-top: 30px;
            box-shadow: var(--card-shadow);
            position: relative;
            height: 400px;
        }
        
        .chart-container.hidden {
            display: none;
        }
        
        /* 결과 카드 그리드 */
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .result-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            position: relative;
        }
        
        .result-card:hover {
            transform: translateY(-3px);
        }
        
        .result-score {
            font-size: 2rem;
            font-weight: bold;
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 10px;
        }
        
        .result-label {
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
        
        /* 8대 영역 특성 카드 */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border-top: 4px solid var(--primary-color);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            color: var(--primary-color);
        }
        
        .feature-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .feature-desc {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        /* 파일 정보 */
        .file-info {
            margin-top: 15px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 12px;
            border-left: 5px solid var(--primary-color);
        }
        
        .file-info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        
        .file-info-item:last-child {
            margin-bottom: 0;
        }
        
        /* 작업 목록 */
        .job-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #eee;
            transition: background 0.3s ease;
        }
        
        .job-item:hover {
            background: rgba(var(--primary-color), 0.05);
        }
        
        .job-item:last-child {
            border-bottom: none;
        }
        
        .job-info {
            flex: 1;
        }
        
        .job-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: var(--dark-color);
        }
        
        .job-meta {
            font-size: 0.9rem;
            color: #666;
        }
        
        /* 향상된 결과 스타일 */
        .strength-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .improvement-hint {
            margin-top: 10px;
            padding: 8px;
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #856404;
        }
        
        .insights-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .insight-section {
            padding: 15px;
            background: white;
            border-radius: 8px;
            border: 1px solid #eee;
        }
        
        .insight-section h5 {
            margin-bottom: 10px;
            font-size: 1.1rem;
        }
        
        .insight-section ul {
            list-style: none;
            padding-left: 0;
        }
        
        .insight-section li {
            margin-bottom: 12px;
            padding-left: 20px;
            position: relative;
        }
        
        .insight-section li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--primary-color);
            font-weight: bold;
        }
        
        .prediction-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }
        
        .prediction-item {
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .prediction-item i {
            font-size: 1.5rem;
        }
        
        /* 디버그 정보 */
        .debug-info {
            background: var(--dark-color);
            color: #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }
        
        .debug-info.show {
            display: block;
        }
        
        .debug-entry {
            margin-bottom: 5px;
            padding: 5px 0;
            border-bottom: 1px solid #3a3a3a;
        }
        
        .debug-time {
            color: var(--secondary-color);
            margin-right: 10px;
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            .status-info {
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .container {
                padding: 20px 10px;
            }
            
            .card {
                padding: 20px;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
            
            .insights-grid,
            .prediction-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary-color);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-color);
        }
    </style>
</head>
<body>
    <!-- 온보딩 오버레이 -->
    <div class="onboarding-overlay" id="onboardingOverlay">
        <div class="onboarding-modal">
            <i class="fas fa-rocket" style="font-size: 3rem; color: var(--primary-color); margin-bottom: 20px;"></i>
            <h2 style="margin-bottom: 20px; color: var(--dark-color);">AIRISS v4.1에 오신 것을 환영합니다!</h2>
            <p style="margin-bottom: 30px; line-height: 1.6; color: #666;">
                OK금융그룹의 AI 기반 인재 분석 시스템으로<br>
                직원의 8대 핵심 역량을 과학적으로 분석합니다.
            </p>
            <div style="display: flex; gap: 15px; justify-content: center;">
                <button class="button" onclick="startTour()">
                    <i class="fas fa-play"></i> 둘러보기 시작
                </button>
                <button class="button secondary" onclick="skipTour()">
                    <i class="fas fa-forward"></i> 건너뛰기
                </button>
            </div>
        </div>
    </div>

    <!-- 알림 시스템 -->
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
                <div>
                    <h1>AIRISS v4.1 Enhanced</h1>
                    <div class="subtitle">OK금융그룹 AI 기반 인재 분석 시스템</div>
                </div>
            </div>
            <div class="status-info">
                <div class="status-item">
                    <i class="fas fa-database"></i>
                    <span>데이터베이스:</span>
                    <span class=\"""" + db_class + """">""" + db_status + """</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-cogs"></i>
                    <span>분석엔진:</span>
                    <span class=\"""" + analysis_class + """">""" + analysis_status + """</span>
                </div>
                <div class="status-item">
                    <i class="fas fa-users"></i>
                    <span>접속자:</span>
                    <span class="status-good" id="connectionCount">0</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="main-grid">
            <!-- 파일 업로드 및 분석 섹션 -->
            <div class="card animate__animated animate__fadeInLeft">
                <h2><i class="fas fa-upload"></i> 파일 업로드 및 분석</h2>
                
                <div class="upload-area" onclick="document.getElementById('fileInput').click()" 
                     ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">Excel 또는 CSV 파일을 업로드하세요</div>
                    <div class="upload-hint">클릭하거나 파일을 여기로 드래그하세요</div>
                    <div class="upload-hint">지원 형식: .xlsx, .xls, .csv (최대 10MB)</div>
                </div>
                
                <input type="file" id="fileInput" style="display: none;" accept=".xlsx,.xls,.csv" onchange="handleFileSelect(event)">
                
                <div style="margin-top: 20px; text-align: center;">
                    <button class="button" onclick="startAnalysis()" id="analyzeBtn" disabled>
                        <i class="fas fa-brain"></i> AI 분석 시작
                    </button>
                    <button class="button secondary" onclick="showSampleData()">
                        <i class="fas fa-file-download"></i> 샘플 데이터
                    </button>
                    <button class="button secondary" onclick="testAnalysisAPI()" id="testApiBtn">
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
            </div>
            
            <!-- 분석 현황 및 결과 섹션 -->
            <div class="card animate__animated animate__fadeInRight">
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
                    <button class="button secondary" onclick="showResultsChart()">
                        <i class="fas fa-chart-radar"></i> 결과 시각화
                    </button>
                    <button class="button secondary" onclick="window.open('/docs', '_blank')">
                        <i class="fas fa-book"></i> API 문서
                    </button>
                </div>
                
                <div id="recentJobs" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- 분석 결과 차트 -->
        <div class="chart-container hidden" id="chartContainer">
            <h3 style="text-align: center; margin-bottom: 20px; color: var(--primary-color);">
                <i class="fas fa-chart-radar"></i> AIRISS 8대 영역 분석 결과
            </h3>
            <canvas id="resultsChart"></canvas>
        </div>
        
        <!-- 최근 분석 결과 카드 -->
        <div class="results-grid" id="resultsGrid" style="display: none;">
            <!-- JavaScript로 동적 생성 -->
        </div>
        
        <!-- AIRISS 8대 영역 소개 -->
        <div class="features-grid">
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.1s;">
                <div class="feature-icon"><i class="fas fa-target"></i></div>
                <div class="feature-title">업무성과 (25%)</div>
                <div class="feature-desc">업무 산출물의 양과 질, 목표 달성도를 종합 분석하여 실질적 기여도를 측정</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.2s;">
                <div class="feature-icon"><i class="fas fa-chart-line"></i></div>
                <div class="feature-title">KPI달성 (20%)</div>
                <div class="feature-desc">핵심성과지표 달성률과 정량적 성과를 AI 기반으로 정밀 평가</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.3s;">
                <div class="feature-icon"><i class="fas fa-smile"></i></div>
                <div class="feature-title">태도마인드 (15%)</div>
                <div class="feature-desc">업무에 대한 열정, 책임감, 성장 마인드셋을 다면적으로 분석</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.4s;">
                <div class="feature-icon"><i class="fas fa-comments"></i></div>
                <div class="feature-title">커뮤니케이션 (15%)</div>
                <div class="feature-desc">의사소통의 명확성, 적시성, 공감능력을 종합 평가</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.5s;">
                <div class="feature-icon"><i class="fas fa-users-cog"></i></div>
                <div class="feature-title">리더십협업 (10%)</div>
                <div class="feature-desc">팀 기여도와 리더십 잠재력, 협업 자세를 과학적으로 측정</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.6s;">
                <div class="feature-icon"><i class="fas fa-graduation-cap"></i></div>
                <div class="feature-title">전문성학습 (8%)</div>
                <div class="feature-desc">전문 지식과 지속적 학습 의지, 기술 역량을 정량화</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.7s;">
                <div class="feature-icon"><i class="fas fa-lightbulb"></i></div>
                <div class="feature-title">창의혁신 (5%)</div>
                <div class="feature-desc">창의적 사고와 혁신 의지, 변화 주도력을 평가</div>
            </div>
            
            <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.8s;">
                <div class="feature-icon"><i class="fas fa-balance-scale"></i></div>
                <div class="feature-title">조직적응 (2%)</div>
                <div class="feature-desc">조직 문화 적응력과 윤리성, 규정 준수를 종합 검증</div>
            </div>
        </div>
        
        <!-- 디버깅 정보 -->
        <div id="debugInfo" class="debug-info">
            <h4 style="margin-bottom: 15px; color: var(--secondary-color);">
                <i class="fas fa-bug"></i> 시스템 디버깅 정보
            </h4>
            <div id="debugLog">시스템 초기화 중...</div>
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <button class="button secondary" onclick="toggleDebugInfo()" style="font-size: 0.9rem; padding: 10px 20px;">
                <i class="fas fa-terminal"></i> 디버깅 정보 토글
            </button>
            <button class="button secondary" onclick="showOnboarding()" style="font-size: 0.9rem; padding: 10px 20px;">
                <i class="fas fa-question-circle"></i> 도움말 보기
            </button>
        </div>
    </div>

    <script>
        // 전역 변수
        let selectedFile = null;
        let currentJobId = null;
        let ws = null;
        let debugMode = false;
        let resultsChart = null;
        let tourStep = 0;
        let lastAnalysisResult = null;
        
        // WebSocket 설정
        const WS_HOST = '""" + WS_HOST + """';
        const SERVER_PORT = '""" + str(SERVER_PORT) + """';
        
        // 샘플 분석 결과 데이터 (테스트용)
        const sampleAnalysisResults = {
            labels: ['업무성과', 'KPI달성', '태도', '커뮤니케이션', '리더십', '협업', '전문성', '창의혁신'],
            datasets: [{
                label: '평균 점수',
                data: [85, 78, 92, 76, 88, 94, 82, 75],
                backgroundColor: 'rgba(255, 87, 34, 0.2)',
                borderColor: 'rgba(255, 87, 34, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(255, 87, 34, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        };
        
        // 🎨 향상된 디버깅 시스템
        function addDebugLog(message, type = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const debugLog = document.getElementById('debugLog');
            const logEntry = document.createElement('div');
            logEntry.className = 'debug-entry';
            
            const iconMap = {
                'info': 'fas fa-info-circle',
                'success': 'fas fa-check-circle',
                'warning': 'fas fa-exclamation-triangle',
                'error': 'fas fa-times-circle'
            };
            
            const colorMap = {
                'info': '#4CAF50',
                'success': '#4CAF50', 
                'warning': '#FF9800',
                'error': '#f44336'
            };
            
            logEntry.innerHTML = `
                <span class="debug-time">[${timestamp}]</span>
                <i class="${iconMap[type] || iconMap.info}" style="color: ${colorMap[type] || colorMap.info}"></i>
                <span style="margin-left: 8px;">${message}</span>
            `;
            
            debugLog.appendChild(logEntry);
            debugLog.scrollTop = debugLog.scrollHeight;
            
            // 콘솔에도 출력
            console.log(`[AIRISS v4.1 Enhanced] ${type.toUpperCase()}: ${message}`);
        }
        
        function toggleDebugInfo() {
            const debugInfo = document.getElementById('debugInfo');
            debugMode = !debugMode;
            if (debugMode) {
                debugInfo.classList.add('show');
                addDebugLog('디버깅 모드 활성화됨', 'success');
            } else {
                debugInfo.classList.remove('show');
            }
        }
        
        // 🎯 온보딩 시스템
        function showOnboarding() {
            document.getElementById('onboardingOverlay').style.display = 'flex';
        }
        
        function skipTour() {
            document.getElementById('onboardingOverlay').style.display = 'none';
            addDebugLog('사용자가 온보딩 투어를 건너뛰었습니다', 'info');
        }
        
        function startTour() {
            document.getElementById('onboardingOverlay').style.display = 'none';
            tourStep = 0;
            nextTourStep();
        }
        
        function nextTourStep() {
            const steps = [
                { selector: '.upload-area', message: '여기에 Excel 또는 CSV 파일을 업로드하세요' },
                { selector: '#analyzeBtn', message: '파일 업로드 후 이 버튼으로 AI 분석을 시작합니다' },
                { selector: '.progress-container', message: '분석 진행률을 실시간으로 확인할 수 있습니다' },
                { selector: '.features-grid', message: 'AIRISS는 8개 핵심 영역을 종합 분석합니다' }
            ];
            
            if (tourStep < steps.length) {
                const step = steps[tourStep];
                highlightElement(step.selector, step.message);
                tourStep++;
                setTimeout(nextTourStep, 3000);
            } else {
                addDebugLog('온보딩 투어 완료', 'success');
                showNotification('온보딩 투어가 완료되었습니다! 이제 파일을 업로드하여 분석을 시작해보세요.', 'success');
            }
        }
        
        function highlightElement(selector, message) {
            const element = document.querySelector(selector);
            if (element) {
                element.style.boxShadow = '0 0 20px rgba(255, 87, 34, 0.8)';
                element.style.transform = 'scale(1.05)';
                
                setTimeout(() => {
                    element.style.boxShadow = '';
                    element.style.transform = '';
                }, 2500);
                
                showNotification(message, 'info');
                addDebugLog(`투어 단계 ${tourStep + 1}: ${message}`, 'info');
            }
        }
        
        // 🔔 향상된 알림 시스템
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            const text = document.getElementById('notificationText');
            const icon = document.getElementById('notificationIcon');
            
            const iconMap = {
                'success': 'fas fa-check-circle',
                'error': 'fas fa-times-circle',
                'warning': 'fas fa-exclamation-triangle',
                'info': 'fas fa-info-circle'
            };
            
            text.textContent = message;
            icon.className = iconMap[type] || iconMap.success;
            notification.className = 'notification ' + type + ' show';
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 5000);
            
            addDebugLog(`알림: ${message}`, type);
        }
        
        // 🌐 WebSocket 연결 시스템
        function connectWebSocket() {
            const clientId = 'enhanced-ui-' + Math.random().toString(36).substr(2, 9);
            addDebugLog(`WebSocket 연결 시도: ${clientId}`, 'info');
            
            ws = new WebSocket(`ws://${WS_HOST}:${SERVER_PORT}/ws/${clientId}?channels=analysis,alerts`);
            
            ws.onopen = () => {
                addDebugLog('WebSocket 연결 성공', 'success');
                updateConnectionCount();
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                addDebugLog(`WebSocket 메시지 수신: ${data.type}`, 'info');
                handleWebSocketMessage(data);
            };
            
            ws.onclose = () => {
                addDebugLog('WebSocket 연결 해제됨', 'warning');
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = (error) => {
                addDebugLog(`WebSocket 오류: ${error}`, 'error');
            };
        }
        
        function handleWebSocketMessage(data) {
            if (data.type === 'analysis_progress' && data.job_id === currentJobId) {
                updateProgress(data.progress, data.processed, data.total);
            } else if (data.type === 'analysis_completed' && data.job_id === currentJobId) {
                updateProgress(100, data.total_processed, data.total_processed);
                showNotification(`분석이 완료되었습니다! 평균 점수: ${data.average_score}점`, 'success');
                setTimeout(() => {
                    loadRecentJobs();
                    showResultsChart();
                }, 1000);
            } else if (data.type === 'analysis_failed' && data.job_id === currentJobId) {
                showNotification('분석 중 오류가 발생했습니다: ' + data.error, 'error');
                resetAnalysisButton();
            }
        }
        
        function updateConnectionCount() {
            fetch('/health')
            .then(response => response.json())
            .then(data => {
                const count = data.components?.connection_count || '0';
                document.getElementById('connectionCount').textContent = count;
                addDebugLog(`연결 수 업데이트: ${count}`, 'info');
            })
            .catch(error => {
                document.getElementById('connectionCount').textContent = '?';
                addDebugLog(`연결 수 업데이트 실패: ${error.message}`, 'error');
            });
        }
        
        // 📁 파일 업로드 시스템
        function handleDragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        }
        
        function handleDragLeave(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                addDebugLog(`드래그앤드롭 파일: ${files[0].name}`, 'info');
                handleFile(files[0]);
            }
        }
        
        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) {
                addDebugLog(`파일 선택: ${file.name}`, 'info');
                handleFile(file);
            }
        }
        
        function handleFile(file) {
            // 파일 크기 체크 (10MB 제한)
            if (file.size > 10 * 1024 * 1024) {
                showNotification('파일 크기가 10MB를 초과합니다. 더 작은 파일을 선택해주세요.', 'error');
                return;
            }
            
            // 파일 형식 체크
            const allowedTypes = ['.xlsx', '.xls', '.csv'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowedTypes.includes(fileExtension)) {
                showNotification('지원하지 않는 파일 형식입니다. Excel 또는 CSV 파일을 선택해주세요.', 'error');
                return;
            }
            
            selectedFile = file;
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileSize').textContent = formatFileSize(file.size);
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('analyzeBtn').disabled = false;
            
            addDebugLog(`파일 검증 완료: ${file.name} (${formatFileSize(file.size)})`, 'success');
            uploadFile(file);
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            document.getElementById('fileStatus').textContent = '업로드 중...';
            addDebugLog('파일 업로드 시작', 'info');
            
            const uploadStartTime = Date.now();
            
            fetch('/upload/upload/', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                addDebugLog(`업로드 응답 상태: ${response.status} ${response.statusText}`, 'info');
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response.json();
            })
            .then(data => {
                const uploadTime = Date.now() - uploadStartTime;
                addDebugLog(`업로드 완료 (${uploadTime}ms): 파일 ID = ${data.id}`, 'success');
                
                if (data.id) {
                    selectedFile.fileId = data.id;
                    document.getElementById('fileStatus').textContent = 
                        `업로드 완료 (${data.total_records || '?'}건 데이터)`;
                    showNotification('파일이 성공적으로 업로드되었습니다.', 'success');
                    
                    if (data.total_records) {
                        addDebugLog(`데이터 분석: 총 ${data.total_records}건, AIRISS 준비=${data.airiss_ready}, 하이브리드 준비=${data.hybrid_ready}`, 'info');
                    }
                } else {
                    throw new Error(data.detail || '업로드 실패: 파일 ID를 받지 못했습니다');
                }
            })
            .catch(error => {
                addDebugLog(`업로드 오류: ${error.message}`, 'error');
                document.getElementById('fileStatus').textContent = '업로드 실패';
                showNotification('파일 업로드 중 오류: ' + error.message, 'error');
            });
        }
        
        // 🧠 분석 시작 시스템
        function startAnalysis() {
            addDebugLog('=== AI 분석 프로세스 시작 ===', 'info');
            
            if (!selectedFile || !selectedFile.fileId) {
                showNotification('먼저 파일을 업로드해주세요.', 'error');
                return;
            }
            
            const analysisData = {
                file_id: selectedFile.fileId,
                sample_size: 10,
                analysis_mode: 'hybrid',
                enable_ai_feedback: false,
                openai_model: 'gpt-3.5-turbo',
                max_tokens: 1200
            };
            
            addDebugLog(`분석 요청 데이터: ${JSON.stringify(analysisData, null, 2)}`, 'info');
            
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = true;
            analyzeBtn.classList.add('loading');
            document.getElementById('progressText').textContent = '분석 시작 중...';
            
            const analysisStartTime = Date.now();
            
            const timeoutId = setTimeout(() => {
                addDebugLog('분석 요청 타임아웃 (30초)', 'error');
                showNotification('분석 시작 요청이 타임아웃되었습니다. 다시 시도해주세요.', 'error');
                resetAnalysisButton();
            }, 30000);
            
            fetch('/analysis/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(analysisData)
            })
            .then(response => {
                clearTimeout(timeoutId);
                const responseTime = Date.now() - analysisStartTime;
                addDebugLog(`분석 API 응답 시간: ${responseTime}ms, 상태: ${response.status}`, 'info');
                
                if (!response.ok) {
                    return response.text().then(text => {
                        addDebugLog(`분석 API 오류 응답: ${text}`, 'error');
                        try {
                            const errorData = JSON.parse(text);
                            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                        } catch (jsonError) {
                            throw new Error(`HTTP ${response.status}: ${text}`);
                        }
                    });
                }
                
                return response.json();
            })
            .then(data => {
                addDebugLog(`분석 시작 성공: Job ID = ${data.job_id}`, 'success');
                
                if (data.job_id) {
                    currentJobId = data.job_id;
                    showNotification('AI 분석이 시작되었습니다. 실시간으로 진행상황을 확인할 수 있습니다.', 'success');
                    updateProgress(0, 0, analysisData.sample_size);
                } else {
                    throw new Error(data.detail || '분석 시작 실패: Job ID를 받지 못했습니다');
                }
            })
            .catch(error => {
                clearTimeout(timeoutId);
                addDebugLog(`분석 시작 오류: ${error.message}`, 'error');
                showNotification('분석 시작 중 오류: ' + error.message, 'error');
                resetAnalysisButton();
            });
        }
        
        function resetAnalysisButton() {
            const analyzeBtn = document.getElementById('analyzeBtn');
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('loading');
            document.getElementById('progressText').textContent = '대기 중';
        }
        
        function updateProgress(percent, processed, total) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = 
                `진행률: ${percent.toFixed(1)}% (${processed}/${total})`;
            
            addDebugLog(`진행률 업데이트: ${percent.toFixed(1)}% (${processed}/${total})`, 'info');
        }
        
        // 📊 향상된 차트 시각화 시스템
        function showResultsChart() {
            const chartContainer = document.getElementById('chartContainer');
            chartContainer.classList.remove('hidden');
            
            if (resultsChart) {
                resultsChart.destroy();
            }
            
            // 실제 분석 데이터가 있으면 사용, 없으면 샘플 데이터
            const analysisData = window.lastAnalysisResult || sampleAnalysisResults;
            
            const ctx = document.getElementById('resultsChart').getContext('2d');
            
            // 그라데이션 배경 생성
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(255, 87, 34, 0.4)');
            gradient.addColorStop(1, 'rgba(248, 156, 38, 0.1)');
            
            resultsChart = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: analysisData.labels,
                    datasets: [{
                        label: '현재 역량',
                        data: analysisData.datasets[0].data,
                        backgroundColor: gradient,
                        borderColor: 'rgba(255, 87, 34, 1)',
                        borderWidth: 3,
                        pointBackgroundColor: 'rgba(255, 87, 34, 1)',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 8,
                        pointHoverRadius: 10
                    }, {
                        label: '목표 수준',
                        data: [85, 85, 85, 85, 85, 85, 85, 85], // 목표선
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        borderColor: 'rgba(76, 175, 80, 0.5)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                stepSize: 20,
                                font: {
                                    size: 11
                                }
                            },
                            grid: {
                                color: 'rgba(255, 87, 34, 0.1)',
                                circular: true
                            },
                            pointLabels: {
                                font: {
                                    size: 13,
                                    weight: 'bold'
                                },
                                color: '#333',
                                padding: 15
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                },
                                color: '#333',
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(255, 87, 34, 0.95)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            cornerRadius: 8,
                            padding: 12,
                            displayColors: false,
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.r;
                                    let emoji = '';
                                    
                                    if (value >= 90) emoji = '🏆';
                                    else if (value >= 80) emoji = '⭐';
                                    else if (value >= 70) emoji = '👍';
                                    else emoji = '📈';
                                    
                                    return `${emoji} ${label}: ${value}점`;
                                },
                                afterLabel: function(context) {
                                    const dimensionName = context.label;
                                    const recommendations = {
                                        '업무성과': '주간 성과 리뷰를 통해 진척도 관리',
                                        'KPI달성': '핵심 지표에 집중하여 효율성 제고',
                                        '태도': '긍정적 피드백 문화 조성',
                                        '커뮤니케이션': '적극적 경청 스킬 개발',
                                        '리더십': '팀 빌딩 활동 참여',
                                        '협업': '크로스팀 프로젝트 참여',
                                        '전문성': '관련 분야 교육 수강',
                                        '창의혁신': '아이디어 브레인스토밍 참여'
                                    };
                                    
                                    if (context.parsed.r < 70) {
                                        return `💡 개선 제안: ${recommendations[dimensionName] || '지속적 역량 개발'}`;
                                    }
                                    return '';
                                }
                            }
                        }
                    },
                    elements: {
                        line: {
                            borderWidth: 3,
                            tension: 0.1
                        },
                        point: {
                            radius: 6,
                            hoverRadius: 10,
                            hoverBorderWidth: 3
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeInOutQuart'
                    }
                }
            });
            
            addDebugLog('향상된 분석 결과 차트 표시 완료', 'success');
            
            // 결과 카드 생성
            createEnhancedResultCards(analysisData);
        }

        // 향상된 결과 카드 생성
        function createEnhancedResultCards(analysisData) {
            const resultsGrid = document.getElementById('resultsGrid');
            const labels = analysisData.labels;
            const data = analysisData.datasets[0].data;
            
            // 전체 평균 계산
            const average = data.reduce((a, b) => a + b, 0) / data.length;
            const grade = getGrade(average);
            
            let cardsHTML = `
                <!-- 종합 점수 카드 -->
                <div class="result-card animate__animated animate__fadeInUp" style="grid-column: span 2; background: linear-gradient(135deg, #FF5722, #F89C26); color: white;">
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 10px;">${grade.badge}</div>
                        <div style="font-size: 2.5rem; font-weight: bold;">${grade.grade} 등급</div>
                        <div style="font-size: 1.2rem; margin-top: 10px;">${grade.description}</div>
                        <div style="font-size: 3rem; margin-top: 20px;">${average.toFixed(1)}점</div>
                        <div style="font-size: 1rem; opacity: 0.9;">종합 점수</div>
                    </div>
                </div>
            `;
            
            // 개별 영역 카드
            labels.forEach((label, index) => {
                const score = data[index];
                const diff = score - average;
                const trend = diff > 5 ? '↑' : diff < -5 ? '↓' : '→';
                const trendColor = diff > 5 ? '#4CAF50' : diff < -5 ? '#f44336' : '#FF9800';
                const strength = score >= 85;
                
                cardsHTML += `
                    <div class="result-card animate__animated animate__fadeInUp" style="animation-delay: ${index * 0.1 + 0.2}s;">
                        ${strength ? '<div class="strength-badge">강점</div>' : ''}
                        <div class="result-score" style="color: ${getScoreColor(score)}">${score}</div>
                        <div class="result-label">${label}</div>
                        <div style="text-align: center; margin-top: 10px;">
                            <span style="color: ${trendColor}; font-size: 1.2rem;">${trend}</span>
                            <span style="font-size: 0.9rem; color: #666; margin-left: 5px;">평균 대비 ${diff > 0 ? '+' : ''}${diff.toFixed(1)}</span>
                        </div>
                        ${score < 70 ? `<div class="improvement-hint">💡 개선 필요</div>` : ''}
                    </div>
                `;
            });
            
            // 인사이트 카드 추가
            cardsHTML += `
                <div class="result-card animate__animated animate__fadeInUp" style="animation-delay: 0.8s; grid-column: span 2; background: #f8f9fa;">
                    <h4 style="color: var(--primary-color); margin-bottom: 15px;"><i class="fas fa-lightbulb"></i> AI 분석 인사이트</h4>
                    <div class="insight-content">
                        ${generateInsights(labels, data, average)}
                    </div>
                </div>
            `;
            
            resultsGrid.innerHTML = cardsHTML;
            resultsGrid.style.display = 'grid';
            
            addDebugLog('향상된 결과 카드 생성 완료', 'success');
        }

        // 등급 판정 함수
        function getGrade(score) {
            if (score >= 95) return { grade: 'S', description: '탁월함 (TOP 1%)', badge: '🏆' };
            if (score >= 90) return { grade: 'A+', description: '매우 우수 (TOP 5%)', badge: '⭐⭐⭐' };
            if (score >= 85) return { grade: 'A', description: '우수 (TOP 10%)', badge: '⭐⭐' };
            if (score >= 80) return { grade: 'B+', description: '양호 (TOP 20%)', badge: '⭐' };
            if (score >= 75) return { grade: 'B', description: '평균 이상 (TOP 30%)', badge: '✨' };
            if (score >= 70) return { grade: 'C+', description: '평균 (TOP 40%)', badge: '👍' };
            if (score >= 60) return { grade: 'C', description: '개선 필요 (TOP 60%)', badge: '📈' };
            return { grade: 'D', description: '집중 관리 필요', badge: '🚨' };
        }

        // 점수별 색상
        function getScoreColor(score) {
            if (score >= 90) return '#4CAF50';
            if (score >= 80) return '#8BC34A';
            if (score >= 70) return '#FF9800';
            if (score >= 60) return '#FF5722';
            return '#f44336';
        }

        // AI 인사이트 생성
        function generateInsights(labels, scores, average) {
            const strengths = [];
            const improvements = [];
            
            labels.forEach((label, index) => {
                if (scores[index] >= 85) {
                    strengths.push({ label, score: scores[index] });
                } else if (scores[index] < 70) {
                    improvements.push({ label, score: scores[index] });
                }
            });
            
            let insights = '<div class="insights-grid">';
            
            // 강점 분석
            if (strengths.length > 0) {
                insights += '<div class="insight-section">';
                insights += '<h5 style="color: #4CAF50;"><i class="fas fa-star"></i> 핵심 강점</h5>';
                insights += '<ul style="margin: 10px 0;">';
                strengths.slice(0, 3).forEach(s => {
                    insights += `<li><strong>${s.label}</strong> - ${s.score}점 (탁월함)</li>`;
                });
                insights += '</ul>';
                insights += '</div>';
            }
            
            // 개선 영역
            if (improvements.length > 0) {
                insights += '<div class="insight-section">';
                insights += '<h5 style="color: #FF5722;"><i class="fas fa-chart-line"></i> 우선 개선 영역</h5>';
                insights += '<ul style="margin: 10px 0;">';
                improvements.slice(0, 3).forEach(i => {
                    const recommendation = getRecommendation(i.label);
                    insights += `<li><strong>${i.label}</strong> - ${i.score}점<br><span style="font-size: 0.9rem; color: #666;">→ ${recommendation}</span></li>`;
                });
                insights += '</ul>';
                insights += '</div>';
            }
            
            // 성과 예측
            insights += '<div class="insight-section" style="grid-column: span 2;">';
            insights += '<h5 style="color: #FF5722;"><i class="fas fa-chart-line"></i> 성과 예측</h5>';
            
            const prediction = predictPerformance(average);
            insights += `
                <div class="prediction-grid">
                    <div class="prediction-item">
                        <i class="fas fa-trending-${prediction.trend}" style="color: ${prediction.color};"></i>
                        <strong>6개월 후 예상 트렌드:</strong> ${prediction.text}
                    </div>
                    <div class="prediction-item">
                        <i class="fas fa-percentage" style="color: #FF9800;"></i>
                        <strong>성공 확률:</strong> ${prediction.probability}%
                    </div>
                    <div class="prediction-item">
                        <i class="fas fa-user-check" style="color: #4CAF50;"></i>
                        <strong>승진 준비도:</strong> ${prediction.readiness}
                    </div>
                    <div class="prediction-item">
                        <i class="fas fa-door-open" style="color: #f44336;"></i>
                        <strong>이직 위험도:</strong> ${prediction.turnover}
                    </div>
                </div>
            `;
            
            insights += '</div>';
            insights += '</div>';
            
            return insights;
        }

        // 영역별 개선 권고사항
        function getRecommendation(dimension) {
            const recommendations = {
                '업무성과': '주간 목표 설정 및 리뷰 프로세스 도입',
                'KPI달성': '핵심 지표 대시보드 활용 및 일일 모니터링',
                '태도': '멘토링 프로그램 참여 및 긍정 심리 교육',
                '커뮤니케이션': '프레젠테이션 스킬 워크샵 수강',
                '리더십': '리더십 코칭 프로그램 참여',
                '협업': '크로스 펑셔널 프로젝트 적극 참여',
                '전문성': 'LinkedIn Learning 또는 Coursera 강의 수강',
                '창의혁신': '디자인 씽킹 워크샵 참여'
            };
            return recommendations[dimension] || '지속적인 자기계발 필요';
        }

        // 성과 예측 함수
        function predictPerformance(avgScore) {
            if (avgScore >= 85) {
                return {
                    trend: 'up',
                    color: '#4CAF50',
                    text: '지속 상승',
                    probability: 85,
                    readiness: '높음',
                    turnover: '낮음 (10%)'
                };
            } else if (avgScore >= 70) {
                return {
                    trend: 'right',
                    color: '#FF9800',
                    text: '안정적 유지',
                    probability: 70,
                    readiness: '보통',
                    turnover: '보통 (25%)'
                };
            } else {
                return {
                    trend: 'down',
                    color: '#f44336',
                    text: '주의 필요',
                    probability: 50,
                    readiness: '낮음',
                    turnover: '높음 (40%)'
                };
            }
        }
        
        // 📋 작업 관리 시스템
        function loadRecentJobs() {
            addDebugLog('최근 작업 목록 조회 시작', 'info');
            
            fetch('/analysis/jobs')
            .then(response => {
                addDebugLog(`작업 목록 응답: ${response.status}`, 'info');
                return response.json();
            })
            .then(jobs => {
                addDebugLog(`작업 수: ${jobs.length}`, 'info');
                displayJobs(jobs);
            })
            .catch(error => {
                addDebugLog(`작업 목록 조회 오류: ${error.message}`, 'error');
                document.getElementById('recentJobs').innerHTML = 
                    '<p style="color: var(--danger-color); text-align: center;"><i class="fas fa-exclamation-triangle"></i> 작업 목록을 불러올 수 없습니다.</p>';
            });
        }
        
        function displayJobs(jobs) {
            const container = document.getElementById('recentJobs');
            
            if (jobs.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #666;">
                        <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 15px; color: #ccc;"></i>
                        <p>최근 분석 작업이 없습니다.</p>
                        <p style="font-size: 0.9rem; margin-top: 10px;">파일을 업로드하여 첫 번째 분석을 시작해보세요!</p>
                    </div>
                `;
                return;
            }
            
            let html = '<h3 style="margin-bottom: 20px; color: var(--primary-color);"><i class="fas fa-history"></i> 최근 분석 작업</h3>';
            
            jobs.forEach((job, index) => {
                const createdDate = new Date(job.created_at || Date.now()).toLocaleString();
                const statusIcon = job.status === 'completed' ? 'fas fa-check-circle' : 
                                 job.status === 'failed' ? 'fas fa-times-circle' : 'fas fa-clock';
                const statusColor = job.status === 'completed' ? 'var(--success-color)' : 
                                  job.status === 'failed' ? 'var(--danger-color)' : 'var(--warning-color)';
                
                html += `
                    <div class="job-item animate__animated animate__fadeInUp" style="animation-delay: ${index * 0.1}s;">
                        <div class="job-info">
                            <div class="job-title">
                                <i class="fas fa-file-excel" style="color: var(--primary-color); margin-right: 8px;"></i>
                                ${job.filename || 'Unknown File'}
                            </div>
                            <div class="job-meta">
                                <i class="${statusIcon}" style="color: ${statusColor}; margin-right: 5px;"></i>
                                ${job.processed || 0}명 분석 완료 • ${createdDate}
                            </div>
                        </div>
                        <div>
                            <button class="button" onclick="viewResults('${job.job_id}')" style="padding: 8px 16px; font-size: 0.9rem;">
                                <i class="fas fa-chart-bar"></i> 결과 보기
                            </button>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        function viewResults(jobId) {
            addDebugLog(`결과 보기: ${jobId}`, 'info');
            showNotification('결과 페이지로 이동합니다...', 'info');
            window.open(`/docs#/analysis/get_analysis_results_analysis_results__job_id__get`, '_blank');
        }
        
        // 🛠️ 시스템 테스트
        function testAnalysisAPI() {
            addDebugLog('=== 시스템 종합 테스트 시작 ===', 'info');
            const testBtn = document.getElementById('testApiBtn');
            testBtn.disabled = true;
            testBtn.textContent = '테스트 중...';
            
            let testResults = [];
            
            // 1. Health Check
            fetch('/health')
            .then(response => response.json())
            .then(data => {
                testResults.push({ name: 'Health Check', status: 'success', details: data.status });
                addDebugLog(`✅ Health Check: ${data.status}`, 'success');
                return fetch('/health/analysis');
            })
            .then(response => response.json())
            .then(data => {
                testResults.push({ name: 'Analysis Engine', status: data.status === 'healthy' ? 'success' : 'error', details: data.status });
                addDebugLog(`✅ Analysis Engine: ${data.status}`, data.status === 'healthy' ? 'success' : 'error');
                return fetch('/health/db');
            })
            .then(response => response.json())
            .then(data => {
                testResults.push({ name: 'Database', status: data.status === 'healthy' ? 'success' : 'error', details: `${data.files} files` });
                addDebugLog(`✅ Database: ${data.status}, 파일 수: ${data.files}`, data.status === 'healthy' ? 'success' : 'error');
                
                // 테스트 결과 요약
                const successCount = testResults.filter(r => r.status === 'success').length;
                const totalCount = testResults.length;
                
                if (successCount === totalCount) {
                    showNotification(`시스템 테스트 완료! 모든 컴포넌트(${totalCount})가 정상 작동 중입니다.`, 'success');
                } else {
                    showNotification(`시스템 테스트 완료. ${successCount}/${totalCount} 컴포넌트가 정상입니다.`, 'warning');
                }
                
                addDebugLog('=== 시스템 테스트 완료 ===', 'success');
            })
            .catch(error => {
                addDebugLog(`시스템 테스트 실패: ${error.message}`, 'error');
                showNotification('시스템 테스트 중 오류 발생: ' + error.message, 'error');
            })
            .finally(() => {
                testBtn.disabled = false;
                testBtn.innerHTML = '<i class="fas fa-tools"></i> 시스템 테스트';
            });
        }
        
        // 📥 샘플 데이터 다운로드
        function showSampleData() {
            addDebugLog('샘플 데이터 생성 및 다운로드', 'info');
            
            const sampleData = `UID,이름,의견,성과등급,KPI점수
EMP001,김철수,매우 열심히 업무에 임하고 동료들과 원활한 소통을 하고 있습니다. 프로젝트 관리 능력이 뛰어나며 팀에 긍정적인 영향을 줍니다. 창의적인 아이디어로 업무 효율을 개선하고 있습니다.,A,85
EMP002,이영희,창의적인 아이디어로 프로젝트를 성공적으로 이끌었습니다. 고객과의 소통이 원활하고 문제 해결 능력이 우수합니다. 전문성 향상을 위해 지속적으로 학습하고 있습니다.,B+,78
EMP003,박민수,시간 관리와 업무 효율성 측면에서 개선이 필요합니다. 하지만 성실한 태도로 꾸준히 발전하고 있습니다. 팀워크는 양호한 편입니다.,C,65
EMP004,최영수,고객과의 소통이 뛰어나고 문제 해결 능력이 우수합니다. 동료들에게 도움을 주는 협업 정신이 훌륭합니다. 리더십 역량도 점차 성장하고 있습니다.,A,92
EMP005,한지민,팀워크가 좋고 협업 능력이 뛰어난 직원입니다. 새로운 기술 습득에 적극적이며 전문성을 지속적으로 향상시키고 있습니다. 혁신적인 사고로 업무 개선에 기여합니다.,B+,80`;
            
            const blob = new Blob([sampleData], { type: 'text/csv;charset=utf-8;' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AIRISS_샘플데이터.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showNotification('AIRISS 샘플 데이터가 다운로드되었습니다. 이 파일을 업로드하여 테스트해보세요!', 'success');
            addDebugLog('샘플 데이터 다운로드 완료', 'success');
        }
        
        // 🚀 페이지 초기화
        document.addEventListener('DOMContentLoaded', function() {
            addDebugLog('AIRISS v4.1 Enhanced UI 초기화 시작', 'info');
            
            // WebSocket 연결
            connectWebSocket();
            
            // 연결 상태 업데이트
            updateConnectionCount();
            
            // 최근 작업 로드
            loadRecentJobs();
            
            // 정기 업데이트 (30초마다)
            setInterval(() => {
                updateConnectionCount();
            }, 30000);
            
            // 온보딩 체크 (첫 방문자용)
            const hasVisited = localStorage.getItem('airiss_visited');
            if (!hasVisited) {
                setTimeout(() => {
                    showOnboarding();
                    localStorage.setItem('airiss_visited', 'true');
                }, 2000);
            }
            
            addDebugLog('초기화 완료 - AIRISS v4.1 Enhanced 시스템 준비됨', 'success');
            showNotification('AIRISS v4.1 Enhanced가 시작되었습니다! 파일을 업로드하여 AI 분석을 시작해보세요.', 'info');
        });
        
        // 페이지 언로드 시 WebSocket 정리
        window.addEventListener('beforeunload', function() {
            if (ws) {
                ws.close();
                addDebugLog('WebSocket 연결 정리 완료', 'info');
            }
        });
        
        // 키보드 단축키
        document.addEventListener('keydown', function(e) {
            // Ctrl + U: 파일 업로드
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
                document.getElementById('fileInput').click();
            }
            
            // Ctrl + D: 디버그 토글
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                toggleDebugInfo();
            }
            
            // F1: 도움말
            if (e.key === 'F1') {
                e.preventDefault();
                showOnboarding();
            }
        });
    </script>
</body>
</html>
"""
    
    return html_template

# 🏠 향상된 메인 페이지 - 고급 차트 시각화 + AI 인사이트
@app.get("/", response_class=HTMLResponse)
async def enhanced_main_interface():
    """AIRISS v4.1 향상된 메인 인터페이스 - 고급 차트 시각화 + AI 인사이트"""
    
    # 현재 상태 확인
    db_status = "정상" if sqlite_service else "오류"
    analysis_status = "정상" if hybrid_analyzer else "오류"
    
    return HTMLResponse(content=get_main_html(db_status, analysis_status))

# 기존 엔드포인트들 유지 (간소화)
@app.get("/api")
async def api_info():
    """API 정보"""
    return {
        "message": "AIRISS v4.1 Enhanced API Server",
        "version": "4.1.0",
        "status": "running",
        "description": "OK금융그룹 AI 기반 인재 분석 시스템 - Enhanced UI/UX Edition with Deep Learning",
        "features": {
            "enhanced_ui": True,
            "chart_visualization": True,
            "sqlite_database": sqlite_service is not None,
            "websocket_realtime": True,
            "airiss_analysis": hybrid_analyzer is not None,
            "hybrid_scoring": True,
            "deep_learning": True,
            "bias_detection": True,
            "performance_prediction": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "status": "healthy",
        "version": "4.1.0",
        "service": "AIRISS v4.1 Enhanced",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "fastapi": "running",
            "websocket_manager": "active",
            "connection_count": len(manager.active_connections),
            "sqlite_service": "active" if sqlite_service else "unavailable",
            "hybrid_analyzer": "active" if hybrid_analyzer else "unavailable",
            "enhanced_ui": "active",
            "ai_insights": "enabled"
        }
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
            "analysis_engine": "AIRISS v4.1 Enhanced",
            "framework_dimensions": 8,
            "hybrid_analysis": True,
            "openai_available": openai_available,
            "enhanced_features": True,
            "deep_learning_ready": True,
            "bias_detection": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

# WebSocket 엔드포인트들
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, channels: str = "analysis,alerts"):
    """메인 WebSocket 엔드포인트"""
    logger.info(f"🔌 Enhanced WebSocket connection: {client_id}")
    channel_list = channels.split(",") if channels else []
    
    try:
        await manager.connect(websocket, client_id, channel_list)
        while True:
            message = await websocket.receive_text()
            await manager.handle_client_message(client_id, message)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Enhanced WebSocket {client_id} disconnected")
    except Exception as e:
        logger.error(f"Enhanced WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)

# 개발자 대시보드 (기존 유지)
@app.get("/dashboard", response_class=HTMLResponse)
async def developer_dashboard():
    """개발자용 대시보드"""
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html><head><title>AIRISS v4.1 Enhanced - 개발자 대시보드</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5;}}
.card{{background:white;padding:20px;margin:15px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}}
h1{{color:#FF5722;}}
</style></head>
<body>
<div class="card">
<h1>🔧 AIRISS v4.1 Enhanced - 개발자 대시보드</h1>
<p><strong>Enhanced UI:</strong> <a href="/" target="_blank">http://{WS_HOST}:{SERVER_PORT}/</a></p>
<p><strong>API 문서:</strong> <a href="/docs" target="_blank">http://{WS_HOST}:{SERVER_PORT}/docs</a></p>
<p><strong>상태:</strong> Enhanced UI/UX 버전 실행 중 - v4.1 Deep Learning Edition</p>
</div>
</body></html>
""")

# 라우터 등록
logger.info("🔧 Enhanced 라우터 등록...")

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

# 메인 실행
if __name__ == "__main__":
    logger.info("🚀 Starting AIRISS v4.1 Enhanced UI/UX Server...")
    logger.info(f"🎨 Enhanced UI: http://{WS_HOST}:{SERVER_PORT}/")
    logger.info(f"📊 Advanced Chart Visualization: Radar + Performance Prediction")
    logger.info(f"🧠 Deep Learning Features: Bias Detection + AI Insights")
    logger.info(f"🎯 User Experience: Smart Notifications + Real-time Progress")
    
    try:
        uvicorn.run(
            "app.main_fixed:app",
            host=SERVER_HOST, 
            port=SERVER_PORT, 
            log_level="info",
            reload=False,
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Enhanced 서버 시작 실패: {e}")
        print(f"\n❌ Enhanced 서버 오류: {e}")
