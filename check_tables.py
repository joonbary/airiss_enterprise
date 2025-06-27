# check_tables.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://airiss_user:airiss_secure_password_2024@localhost:5432/airiss_db"

async def check_tables():
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.connect() as conn:
        # 각 테이블의 컬럼 정보 확인
        tables = ['file_uploads', 'analysis_jobs', 'employee_scores']
        
        for table in tables:
            print(f"\n📊 {table} 테이블 구조:")
            result = await conn.execute(
                text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
            )
            columns = result.fetchall()
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"   - {col[0]}: {col[1]} ({nullable})")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())