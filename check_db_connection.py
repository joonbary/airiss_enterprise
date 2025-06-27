# check_db_connection.py
import sqlite3
import os

def check_db():
    print("🔍 데이터베이스 연결 확인")
    
    # 가능한 위치들
    locations = [
        ".",
        "app",
        "data",
        os.path.dirname(os.path.abspath(__file__))
    ]
    
    for loc in locations:
        db_path = os.path.join(loc, "airiss.db")
        if os.path.exists(db_path):
            print(f"✅ DB 발견: {db_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 테이블 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   테이블: {[t[0] for t in tables]}")
            
            # files 테이블 데이터 확인
            try:
                cursor.execute("SELECT COUNT(*) FROM files")
                count = cursor.fetchone()[0]
                print(f"   파일 레코드 수: {count}")
            except:
                print("   ❌ files 테이블 없음")
            
            conn.close()

if __name__ == "__main__":
    check_db()