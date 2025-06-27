# scripts/init_db.py
"""데이터베이스 초기화 스크립트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models import Base

def init_database():
    """데이터베이스 테이블 생성"""
    print("데이터베이스 초기화 시작...")
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성 완료!")

if __name__ == "__main__":
    init_database()