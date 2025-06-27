# app/db/init_db.py
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Base와 모든 모델 import
from app.models.base import Base
from app.models.file_upload import FileUpload
from app.models.analysis_job import AnalysisJob
from app.models.employee_score import EmployeeScore

DATABASE_URL = "postgresql+asyncpg://airiss_user:airiss_secure_password_2024@localhost:5432/airiss_db"

async def create_tables():
    """AIRISS v4 테이블 생성"""
    print("🔄 AIRISS v4 테이블 생성 시작...")
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # 테이블 생성
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ 테이블 생성 완료!")
        
        # 생성된 테이블 확인
        async with engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
            )
            tables = result.fetchall()
            
            print(f"\n📋 생성된 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"   - {table[0]}")
                
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())