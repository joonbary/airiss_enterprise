# app/core/dependencies.py
from app.db.sqlite_service import SQLiteService, sqlite_service

async def get_sqlite_service() -> SQLiteService:
    """SQLiteService 의존성 주입"""
    return sqlite_service