# app/middleware/monitoring.py
# AIRISS v4.0 통합 모니터링 미들웨어 - 성능/에러/사용자 분석

import time
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import asyncio
import psutil
import sqlite3
from pathlib import Path

# 로깅 설정
logger = logging.getLogger(__name__)

class AIRISSMonitoringMiddleware(BaseHTTPMiddleware):
    """AIRISS v4.0 통합 모니터링 미들웨어"""
    
    def __init__(self, app, db_path: str = "monitoring.db"):
        super().__init__(app)
        self.db_path = db_path
        self.init_monitoring_db()
        
        # 성능 메트릭 저장용
        self.metrics = {
            "requests_total": 0,
            "requests_failed": 0,
            "response_times": [],
            "active_connections": 0,
            "memory_usage": [],
            "cpu_usage": []
        }
        
        # 백그라운드 모니터링 태스크 시작
        asyncio.create_task(self.background_monitoring())
    
    def init_monitoring_db(self):
        """모니터링 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 요청 로그 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    method TEXT,
                    path TEXT,
                    status_code INTEGER,
                    response_time REAL,
                    user_agent TEXT,
                    ip_address TEXT,
                    user_id TEXT,
                    error_details TEXT
                )
            ''')
            
            # 시스템 메트릭 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    disk_percent REAL,
                    active_connections INTEGER,
                    requests_per_minute REAL
                )
            ''')
            
            # 에러 로그 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    error_type TEXT,
                    error_message TEXT,
                    traceback TEXT,
                    request_path TEXT,
                    user_id TEXT,
                    severity TEXT DEFAULT 'ERROR'
                )
            ''')
            
            # 사용자 활동 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    action TEXT,
                    details TEXT,
                    session_id TEXT,
                    ip_address TEXT
                )
            ''')
            
            # 성능 지표 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT,
                    metric_value REAL,
                    metric_unit TEXT,
                    tags TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ 모니터링 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 모니터링 DB 초기화 실패: {e}")
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리 및 모니터링"""
        start_time = time.time()
        
        # 요청 정보 수집
        user_agent = request.headers.get("user-agent", "")
        ip_address = self.get_client_ip(request)
        user_id = self.extract_user_id(request)
        
        # 활성 연결 수 증가
        self.metrics["active_connections"] += 1
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 시간 계산
            response_time = time.time() - start_time
            self.metrics["response_times"].append(response_time)
            
            # 요청 로그 저장
            await self.log_request(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                response_time=response_time,
                user_agent=user_agent,
                ip_address=ip_address,
                user_id=user_id
            )
            
            # 성능 메트릭 업데이트
            self.metrics["requests_total"] += 1
            if response.status_code >= 400:
                self.metrics["requests_failed"] += 1
            
            # 사용자 활동 로그
            if user_id:
                await self.log_user_activity(
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    ip_address=ip_address
                )
            
            return response
            
        except Exception as e:
            # 에러 처리 및 로깅
            response_time = time.time() - start_time
            
            await self.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=traceback.format_exc(),
                request_path=str(request.url.path),
                user_id=user_id
            )
            
            self.metrics["requests_failed"] += 1
            
            # 에러 응답 생성
            return Response(
                content=json.dumps({
                    "error": "Internal Server Error",
                    "message": "시스템 오류가 발생했습니다.",
                    "timestamp": datetime.now().isoformat()
                }),
                status_code=500,
                media_type="application/json"
            )
        
        finally:
            # 활성 연결 수 감소
            self.metrics["active_connections"] -= 1
    
    def get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return str(request.client.host) if request.client else "unknown"
    
    def extract_user_id(self, request: Request) -> Optional[str]:
        """요청에서 사용자 ID 추출 (향후 인증 시스템과 연동)"""
        # 현재는 세션 기반으로 임시 ID 생성
        session_id = request.headers.get("x-session-id")
        if session_id:
            return f"session_{session_id}"
        
        # IP 기반 임시 ID
        return f"ip_{self.get_client_ip(request)}"
    
    async def log_request(self, method: str, path: str, status_code: int, 
                         response_time: float, user_agent: str, 
                         ip_address: str, user_id: Optional[str]):
        """요청 로그 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO request_logs 
                (method, path, status_code, response_time, user_agent, ip_address, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (method, path, status_code, response_time, user_agent, ip_address, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"요청 로그 저장 실패: {e}")
    
    async def log_error(self, error_type: str, error_message: str, 
                       traceback: str, request_path: str, user_id: Optional[str]):
        """에러 로그 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO error_logs 
                (error_type, error_message, traceback, request_path, user_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (error_type, error_message, traceback, request_path, user_id))
            
            conn.commit()
            conn.close()
            
            logger.error(f"에러 발생: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"에러 로그 저장 실패: {e}")
    
    async def log_user_activity(self, user_id: str, action: str, 
                               ip_address: str, details: str = None):
        """사용자 활동 로그 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activities 
                (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"사용자 활동 로그 저장 실패: {e}")
    
    async def background_monitoring(self):
        """백그라운드 시스템 모니터링"""
        while True:
            try:
                # 시스템 메트릭 수집
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # 요청 속도 계산 (분당 요청 수)
                current_time = time.time()
                recent_requests = len([
                    rt for rt in self.metrics["response_times"][-60:]  # 최근 60초
                ])
                
                # 메트릭 저장
                await self.save_system_metrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_percent=disk.percent,
                    active_connections=self.metrics["active_connections"],
                    requests_per_minute=recent_requests
                )
                
                # 메모리 정리 (오래된 데이터 제거)
                if len(self.metrics["response_times"]) > 1000:
                    self.metrics["response_times"] = self.metrics["response_times"][-500:]
                
                # 60초마다 실행
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"백그라운드 모니터링 오류: {e}")
                await asyncio.sleep(60)
    
    async def save_system_metrics(self, cpu_percent: float, memory_percent: float,
                                 memory_used_mb: float, disk_percent: float,
                                 active_connections: int, requests_per_minute: float):
        """시스템 메트릭 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, memory_used_mb, disk_percent, 
                 active_connections, requests_per_minute)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (cpu_percent, memory_percent, memory_used_mb, disk_percent,
                  active_connections, requests_per_minute))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"시스템 메트릭 저장 실패: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """현재 메트릭 요약 반환"""
        avg_response_time = (
            sum(self.metrics["response_times"][-100:]) / 
            len(self.metrics["response_times"][-100:])
            if self.metrics["response_times"] else 0
        )
        
        error_rate = (
            (self.metrics["requests_failed"] / self.metrics["requests_total"]) * 100
            if self.metrics["requests_total"] > 0 else 0
        )
        
        return {
            "total_requests": self.metrics["requests_total"],
            "failed_requests": self.metrics["requests_failed"],
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "active_connections": self.metrics["active_connections"],
            "uptime_seconds": time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }


class MonitoringAPI:
    """모니터링 데이터 조회 API"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """모니터링 대시보드 데이터 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 시간 범위 설정
            since = datetime.now() - timedelta(hours=hours)
            
            # 요청 통계
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as failed_requests,
                    AVG(response_time) as avg_response_time,
                    MAX(response_time) as max_response_time
                FROM request_logs 
                WHERE timestamp > ?
            ''', (since,))
            
            request_stats = cursor.fetchone()
            
            # 시간별 요청 수
            cursor.execute('''
                SELECT 
                    strftime('%H', timestamp) as hour,
                    COUNT(*) as request_count
                FROM request_logs 
                WHERE timestamp > ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            ''', (since,))
            
            hourly_requests = [
                {"hour": row[0], "requests": row[1]} 
                for row in cursor.fetchall()
            ]
            
            # 최근 에러 로그
            cursor.execute('''
                SELECT error_type, error_message, timestamp, request_path
                FROM error_logs 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (since,))
            
            recent_errors = [
                {
                    "type": row[0],
                    "message": row[1],
                    "timestamp": row[2],
                    "path": row[3]
                }
                for row in cursor.fetchall()
            ]
            
            # 시스템 메트릭 (최근 값)
            cursor.execute('''
                SELECT cpu_percent, memory_percent, memory_used_mb, 
                       disk_percent, active_connections, requests_per_minute
                FROM system_metrics 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', )
            
            system_metrics = cursor.fetchone()
            
            # 인기 페이지
            cursor.execute('''
                SELECT path, COUNT(*) as hits
                FROM request_logs 
                WHERE timestamp > ? AND status_code < 400
                GROUP BY path
                ORDER BY hits DESC
                LIMIT 10
            ''', (since,))
            
            popular_pages = [
                {"path": row[0], "hits": row[1]}
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                "request_stats": {
                    "total": request_stats[0] or 0,
                    "failed": request_stats[1] or 0,
                    "error_rate": round((request_stats[1] / request_stats[0] * 100) if request_stats[0] > 0 else 0, 2),
                    "avg_response_time": round((request_stats[2] or 0) * 1000, 2),  # ms로 변환
                    "max_response_time": round((request_stats[3] or 0) * 1000, 2)
                },
                "hourly_requests": hourly_requests,
                "recent_errors": recent_errors,
                "system_metrics": {
                    "cpu_percent": system_metrics[0] if system_metrics else 0,
                    "memory_percent": system_metrics[1] if system_metrics else 0,
                    "memory_used_mb": system_metrics[2] if system_metrics else 0,
                    "disk_percent": system_metrics[3] if system_metrics else 0,
                    "active_connections": system_metrics[4] if system_metrics else 0,
                    "requests_per_minute": system_metrics[5] if system_metrics else 0
                },
                "popular_pages": popular_pages,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"대시보드 데이터 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """성능 트렌드 데이터 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since = datetime.now() - timedelta(days=days)
            
            # 일별 성능 지표
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(response_time) as avg_response_time,
                    COUNT(*) as total_requests,
                    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as error_count
                FROM request_logs 
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (since,))
            
            daily_performance = [
                {
                    "date": row[0],
                    "avg_response_time": round(row[1] * 1000, 2) if row[1] else 0,
                    "total_requests": row[2],
                    "error_rate": round((row[3] / row[2] * 100) if row[2] > 0 else 0, 2)
                }
                for row in cursor.fetchall()
            ]
            
            # 시스템 리소스 트렌드
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    AVG(cpu_percent) as avg_cpu,
                    AVG(memory_percent) as avg_memory,
                    AVG(requests_per_minute) as avg_rpm
                FROM system_metrics 
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (since,))
            
            resource_trends = [
                {
                    "date": row[0],
                    "avg_cpu": round(row[1], 2) if row[1] else 0,
                    "avg_memory": round(row[2], 2) if row[2] else 0,
                    "avg_requests_per_minute": round(row[3], 2) if row[3] else 0
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                "daily_performance": daily_performance,
                "resource_trends": resource_trends,
                "period_days": days,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"성능 트렌드 조회 실패: {e}")
            return {"error": str(e)}


# FastAPI 라우터에 추가할 모니터링 엔드포인트들
from fastapi import APIRouter

monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@monitoring_router.get("/dashboard")
async def get_monitoring_dashboard(hours: int = 24):
    """모니터링 대시보드 데이터 조회"""
    api = MonitoringAPI()
    return api.get_dashboard_data(hours)

@monitoring_router.get("/performance")
async def get_performance_trends(days: int = 7):
    """성능 트렌드 데이터 조회"""
    api = MonitoringAPI()
    return api.get_performance_trends(days)

@monitoring_router.get("/health/detailed")
async def get_detailed_health():
    """상세 헬스 체크"""
    try:
        # 시스템 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 데이터베이스 연결 테스트
        db_healthy = True
        try:
            conn = sqlite3.connect("monitoring.db")
            conn.close()
        except:
            db_healthy = False
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "monitoring": "healthy"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }