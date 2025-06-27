"""
데이터베이스 연결 및 세션 관리
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

# Base 클래스 생성
Base = declarative_base()

# 전역 변수
engine = None
AsyncSessionLocal = None

async def init_db():
    """데이터베이스 초기화"""
    global engine, AsyncSessionLocal
    
    try:
        from app.core.config.settings import settings
        
        # 비동기 엔진 생성
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True
        )
        
        # 세션 팩토리 생성
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("데이터베이스 연결 성공")
        
        # 테이블 생성 (개발 환경에서만)
        if settings.DEBUG:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("데이터베이스 테이블 생성 완료")
                
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()