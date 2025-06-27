# check_db_status.py
import os
import sqlite3

print("🔍 데이터베이스 상태 확인\n")

# DB 파일 찾기
db_locations = ["airiss.db", "app/airiss.db", "./airiss.db"]
db_found = False

for location in db_locations:
    if os.path.exists(location):
        print(f"✅ DB 파일 발견: {location}")
        print(f"   크기: {os.path.getsize(location) / 1024:.2f} KB")
        
        # 테이블 확인
        conn = sqlite3.connect(location)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"   테이블: {tables}")
        
        # 각 테이블의 레코드 수 확인
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count}개 레코드")
        
        conn.close()
        db_found = True
        break

if not db_found:
    print("❌ 데이터베이스 파일을 찾을 수 없습니다!")