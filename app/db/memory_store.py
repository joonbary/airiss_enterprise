# app/db/memory_store.py
"""
AIRISS v4.0 메모리 기반 데이터 저장소
- 실제 DB 연동 전 임시 저장소
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class MemoryStore:
    """메모리 기반 임시 저장소"""
    
    def __init__(self):
        self.files: Dict[str, Dict[str, Any]] = {}
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()
    
    async def create_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보 저장"""
        async with self.lock:
            file_id = str(uuid.uuid4())
            self.files[file_id] = {
                **file_data,
                'id': file_id,
                'upload_time': datetime.now()
            }
            logger.info(f"파일 저장: {file_id}")
            return file_id
    
    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보 조회"""
        async with self.lock:
            return self.files.get(file_id)
    
    async def delete_file(self, file_id: str) -> bool:
        """파일 삭제"""
        async with self.lock:
            if file_id in self.files:
                del self.files[file_id]
                logger.info(f"파일 삭제: {file_id}")
                return True
            return False
    
    async def list_files(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """파일 목록 조회"""
        async with self.lock:
            files = list(self.files.values())
            # 최신순 정렬
            files.sort(key=lambda x: x['upload_time'], reverse=True)
            
            # 페이징
            start = offset
            end = offset + limit
            
            # 필요한 정보만 반환
            return [
                {
                    'file_id': f['id'],
                    'filename': f['filename'],
                    'size': f['size'],
                    'total_records': f['total_records'],
                    'upload_time': f['upload_time'].isoformat()
                }
                for f in files[start:end]
            ]
    
    async def create_job(self, job_data: Dict[str, Any]) -> str:
        """작업 생성"""
        async with self.lock:
            job_id = str(uuid.uuid4())
            self.jobs[job_id] = {
                **job_data,
                'id': job_id,
                'created_at': datetime.now()
            }
            logger.info(f"작업 생성: {job_id}")
            return job_id
    
    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 조회"""
        async with self.lock:
            return self.jobs.get(job_id)
    
    async def update_job(self, job_id: str, updates: Dict[str, Any]) -> bool:
        """작업 업데이트"""
        async with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(updates)
                self.jobs[job_id]['updated_at'] = datetime.now()
                return True
            return False
    
    async def delete_job(self, job_id: str) -> bool:
        """작업 삭제"""
        async with self.lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                logger.info(f"작업 삭제: {job_id}")
                return True
            return False
    
    async def list_jobs(self, status: Optional[str] = None, 
                       limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """작업 목록 조회"""
        async with self.lock:
            jobs = list(self.jobs.values())
            
            # 상태 필터링
            if status:
                jobs = [j for j in jobs if j.get('status') == status]
            
            # 최신순 정렬
            jobs.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
            
            # 페이징
            start = offset
            end = offset + limit
            
            return jobs[start:end]
    
    async def cleanup_old_data(self, hours: int = 24):
        """오래된 데이터 정리"""
        async with self.lock:
            now = datetime.now()
            
            # 오래된 파일 삭제
            file_ids_to_delete = []
            for file_id, file_data in self.files.items():
                if (now - file_data['upload_time']).total_seconds() > hours * 3600:
                    file_ids_to_delete.append(file_id)
            
            for file_id in file_ids_to_delete:
                del self.files[file_id]
                logger.info(f"오래된 파일 삭제: {file_id}")
            
            # 오래된 작업 삭제
            job_ids_to_delete = []
            for job_id, job_data in self.jobs.items():
                if (now - job_data['created_at']).total_seconds() > hours * 3600:
                    job_ids_to_delete.append(job_id)
            
            for job_id in job_ids_to_delete:
                del self.jobs[job_id]
                logger.info(f"오래된 작업 삭제: {job_id}")
            
            return {
                'deleted_files': len(file_ids_to_delete),
                'deleted_jobs': len(job_ids_to_delete)
            }

# 전역 인스턴스
memory_store = MemoryStore()