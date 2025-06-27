"""
기본 Repository 클래스
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """기본 CRUD 작업을 위한 Repository"""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """ID로 단일 레코드 조회"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """모든 레코드 조회 (페이지네이션)"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """새 레코드 생성"""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def update(self, id: uuid.UUID, **kwargs) -> Optional[ModelType]:
        """레코드 업데이트"""
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.db.commit()
        return await self.get(id)
    
    async def delete(self, id: uuid.UUID) -> bool:
        """레코드 삭제"""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self) -> int:
        """전체 레코드 수"""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar()