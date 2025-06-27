# test_db.py
import asyncio
import asyncpg
from redis import asyncio as aioredis

async def test_connections():
    # PostgreSQL 테스트
    print("🔄 PostgreSQL 연결 테스트...")
    try:
        conn = await asyncpg.connect(
            'postgresql://airiss_user:airiss_secure_password_2024@localhost:5432/airiss_db'
        )
        version = await conn.fetchval('SELECT version()')
        print(f"✅ PostgreSQL 연결 성공!")
        print(f"   버전: {version[:50]}...")
        await conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
    
    print("\n🔄 Redis 연결 테스트...")
    try:
        redis = await aioredis.from_url(
            "redis://:airiss_redis_password_2024@localhost:6379",
            decode_responses=True
        )
        pong = await redis.ping()
        info = await redis.info('server')
        print(f"✅ Redis 연결 성공! (PING: {pong})")
        print(f"   버전: Redis {info['redis_version']}")
        await redis.close()
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_connections())