# app/core/redis_client.py
"""Redis 클라이언트 설정"""

import redis
import json
from typing import Optional, Any
from app.core.config import settings

class RedisClient:
    def __init__(self):
        # get_redis_url() 메서드 호출
        redis_url = settings.get_redis_url()
        self.client = redis.from_url(redis_url, decode_responses=True)
    
    def set_job_status(self, job_id: str, status: dict, expire: int = 3600):
        """작업 상태 저장"""
        self.client.setex(
            f"job:{job_id}",
            expire,
            json.dumps(status)
        )
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """작업 상태 조회"""
        data = self.client.get(f"job:{job_id}")
        return json.loads(data) if data else None
    
    def update_job_progress(self, job_id: str, processed: int, total: int):
        """작업 진행률 업데이트"""
        data = self.get_job_status(job_id)
        if data:
            data["processed"] = processed
            data["progress"] = round((processed / total) * 100, 1)
            self.set_job_status(job_id, data)
    
    def cache_analysis_result(self, uid: str, result: dict, expire: int = 7200):
        """분석 결과 캐싱"""
        self.client.setex(
            f"result:{uid}",
            expire,
            json.dumps(result)
        )
    
    def get_cached_result(self, uid: str) -> Optional[dict]:
        """캐시된 결과 조회"""
        data = self.client.get(f"result:{uid}")
        return json.loads(data) if data else None

# 싱글톤 인스턴스
redis_client = RedisClient()