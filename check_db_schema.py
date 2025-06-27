# check_db_schema.py
# SQLite 데이터베이스 스키마 확인 및 문제 진단

import sqlite3
import os
from datetime import datetime

def check_database_schema():
    """데이터베이스 스키마 확인"""
    db_path = "airiss.db"
    
    print("🔍 AIRISS v4.0 데이터베이스 스키마 진단")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일이 존재하지 않습니다: {db_path}")
        print("💡 해결방법: init_database.py를 실행하여 데이터베이스를 생성하세요")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 테이블 목록 확인
        print("📋 1. 테이블 목록:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ❌ 테이블이 존재하지 않습니다")
            return False
        
        for table in tables:
            print(f"   ✅ {table[0]}")
        
        # 2. files 테이블 스키마 확인
        print("\n📋 2. files 테이블 스키마:")
        cursor.execute("PRAGMA table_info(files);")
        files_columns = cursor.fetchall()
        
        if not files_columns:
            print("   ❌ files 테이블이 존재하지 않습니다")
            return False
        
        print("   컬럼 정보:")
        for col in files_columns:
            print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # 3. 필요한 컬럼 확인
        required_columns = ['id', 'filename', 'upload_time', 'total_records', 
                          'columns', 'uid_columns', 'opinion_columns', 
                          'quantitative_columns', 'file_data']
        
        existing_columns = [col[1] for col in files_columns]
        missing_columns = [col for col in required_columns if col not in existing_columns]
        
        print("\n📋 3. 컬럼 일치성 검사:")
        if missing_columns:
            print("   ❌ 누락된 컬럼들:")
            for col in missing_columns:
                print(f"   - {col}")
            
            print("\n💡 해결방법:")
            print("   1. 데이터베이스 삭제 후 재생성: rm airiss.db && python init_database.py")
            print("   2. 또는 스키마 마이그레이션 실행")
            return False
        else:
            print("   ✅ 모든 필요한 컬럼이 존재합니다")
        
        # 4. jobs 테이블 확인
        print("\n📋 4. jobs 테이블 스키마:")
        cursor.execute("PRAGMA table_info(jobs);")
        jobs_columns = cursor.fetchall()
        
        if jobs_columns:
            for col in jobs_columns:
                print(f"   - {col[1]} ({col[2]})")
        else:
            print("   ❌ jobs 테이블이 존재하지 않습니다")
        
        # 5. results 테이블 확인
        print("\n📋 5. results 테이블 스키마:")
        cursor.execute("PRAGMA table_info(results);")
        results_columns = cursor.fetchall()
        
        if results_columns:
            for col in results_columns:
                print(f"   - {col[1]} ({col[2]})")
        else:
            print("   ❌ results 테이블이 존재하지 않습니다")
        
        # 6. 데이터 현황
        print("\n📋 6. 데이터 현황:")
        cursor.execute("SELECT COUNT(*) FROM files")
        files_count = cursor.fetchone()[0]
        print(f"   파일: {files_count}개")
        
        cursor.execute("SELECT COUNT(*) FROM jobs")
        jobs_count = cursor.fetchone()[0]
        print(f"   작업: {jobs_count}개")
        
        cursor.execute("SELECT COUNT(*) FROM results")
        results_count = cursor.fetchone()[0]
        print(f"   결과: {results_count}개")
        
        conn.close()
        
        print("\n" + "=" * 60)
        if missing_columns:
            print("❌ 스키마 문제 발견됨")
            return False
        else:
            print("✅ 데이터베이스 스키마 정상")
            return True
            
    except Exception as e:
        print(f"❌ 데이터베이스 확인 중 오류: {e}")
        return False

def fix_database_schema():
    """데이터베이스 스키마 문제 해결"""
    print("\n🔧 데이터베이스 스키마 문제 해결 중...")
    
    # 기존 데이터베이스 백업
    if os.path.exists("airiss.db"):
        backup_name = f"airiss_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            import shutil
            shutil.copy("airiss.db", backup_name)
            print(f"💾 기존 DB 백업: {backup_name}")
        except Exception as e:
            print(f"⚠️ 백업 실패: {e}")
    
    # 새 데이터베이스 생성
    try:
        if os.path.exists("airiss.db"):
            os.remove("airiss.db")
            print("🗑️ 기존 데이터베이스 삭제됨")
        
        # SQLiteService를 사용한 초기화
        import asyncio
        
        async def init_db():
            from app.db.sqlite_service import SQLiteService
            service = SQLiteService()
            await service.init_database()
            print("✅ 새 데이터베이스 생성 완료")
        
        asyncio.run(init_db())
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 재생성 실패: {e}")
        return False

def main():
    if check_database_schema():
        print("🎉 데이터베이스가 정상적으로 구성되어 있습니다!")
    else:
        print("\n🔧 스키마 문제를 해결하시겠습니까? (y/N): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            if fix_database_schema():
                print("✅ 데이터베이스 문제 해결 완료!")
                print("🚀 이제 python test_airiss_v4.py를 다시 실행해보세요")
            else:
                print("❌ 문제 해결 실패")
        else:
            print("💡 수동 해결 방법:")
            print("   1. rm airiss.db")
            print("   2. python -c \"import asyncio; from app.db.sqlite_service import SQLiteService; asyncio.run(SQLiteService().init_database())\"")
            print("   3. python test_airiss_v4.py")

if __name__ == "__main__":
    main()
