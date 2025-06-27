"""
AnalysisJob Repository
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import uuid

from app.db.repositories.base import BaseRepository
from app.models.models import AnalysisJob, JobStatus
from sqlalchemy.ext.asyncio import AsyncSession

class JobRepository(BaseRepository[AnalysisJob]):
    """분석 작업 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(AnalysisJob, db)
    
    async def get_with_scores(self, job_id: uuid.UUID) -> Optional[AnalysisJob]:
        """점수 정보와 함께 작업 조회"""
        result = await self.db.execute(
            select(AnalysisJob)
            .options(selectinload(AnalysisJob.scores))
            .where(AnalysisJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_status(self, status: JobStatus) -> List[AnalysisJob]:
        """상태별 작업 조회"""
        result = await self.db.execute(
            select(AnalysisJob).where(AnalysisJob.status == status)
        )
        return list(result.scalars().all())
    
    async def get_completed_jobs(self, limit: int = 50) -> List[AnalysisJob]:
        """완료된 작업 목록 조회"""
        result = await self.db.execute(
            select(AnalysisJob)
            .where(AnalysisJob.status == JobStatus.COMPLETED)
            .order_by(AnalysisJob.completed_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_progress(
        self, 
        job_id: uuid.UUID, 
        processed: int, 
        failed: int = 0
    ) -> None:
        """작업 진행 상황 업데이트"""
        await self.db.execute(
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                processed_records=processed,
                failed_records=failed
            )
        )
        await self.db.commit()
    
    async def complete_job(
        self, 
        job_id: uuid.UUID, 
        average_score: float
    ) -> None:
        """작업 완료 처리"""
        await self.db.execute(
            update(AnalysisJob)
            .where(AnalysisJob.id == job_id)
            .values(
                status=JobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                average_score=average_score
            )
        )
        await self.db.commit()