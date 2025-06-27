# app/services/analysis_service.py
"""
AIRISS v4.0 분석 서비스
- 분석 작업 관리 및 처리
- WebSocket과 연동
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AnalysisService:
    """분석 서비스 - 분석 작업의 라이프사이클 관리"""
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.active_jobs = {}
        logger.info("✅ AnalysisService 초기화 완료")
    
    async def start_analysis(self, job_id: str, job_data: Dict[str, Any]):
        """분석 작업 시작"""
        try:
            self.active_jobs[job_id] = {
                'status': 'processing',
                'start_time': datetime.now(),
                'data': job_data
            }
            
            if self.websocket_manager:
                await self.websocket_manager.send_alert(
                    "info",
                    f"분석 시작: {job_id}",
                    {"job_id": job_id}
                )
            
            logger.info(f"✅ 분석 작업 시작: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 분석 시작 오류: {e}")
            return False
    
    async def update_progress(self, job_id: str, progress: float, details: Dict = None):
        """분석 진행률 업데이트"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['progress'] = progress
                self.active_jobs[job_id]['last_update'] = datetime.now()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_analysis_progress(job_id, {
                        "progress": progress,
                        "details": details or {}
                    })
            
        except Exception as e:
            logger.error(f"❌ 진행률 업데이트 오류: {e}")
    
    async def complete_analysis(self, job_id: str, results: Dict[str, Any]):
        """분석 완료 처리"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'completed'
                self.active_jobs[job_id]['end_time'] = datetime.now()
                self.active_jobs[job_id]['results'] = results
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "success",
                        f"분석 완료: {job_id}",
                        {"job_id": job_id, "results_count": len(results.get('data', []))}
                    )
                
                logger.info(f"✅ 분석 완료: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ 분석 완료 처리 오류: {e}")
    
    async def fail_analysis(self, job_id: str, error: str):
        """분석 실패 처리"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'failed'
                self.active_jobs[job_id]['error'] = error
                self.active_jobs[job_id]['end_time'] = datetime.now()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "error",
                        f"분석 실패: {job_id}",
                        {"job_id": job_id, "error": error}
                    )
                
                logger.error(f"❌ 분석 실패: {job_id} - {error}")
            
        except Exception as e:
            logger.error(f"❌ 분석 실패 처리 오류: {e}")
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        return self.active_jobs.get(job_id)
    
    def list_active_jobs(self) -> Dict[str, Any]:
        """활성 작업 목록"""
        return {
            "active_jobs": len(self.active_jobs),
            "jobs": list(self.active_jobs.keys())
        }