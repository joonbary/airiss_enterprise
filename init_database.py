# init_database.py
import sqlite3
import os
from datetime import datetime

def init_database():
    """AIRISS v4.0 SQLite 데이터베이스 초기화"""
    
    # DB 파일 경로
    db_path = "airiss.db"
    
    print(f"🗄️ SQLite 데이터베이스 생성 시작...")
    
    # 기존 파일 백업
    if os.path.exists(db_path):
        backup_name = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(db_path, backup_name)
        print(f"📦 기존 DB 백업: {backup_name}")
    
    # 새 데이터베이스 생성
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # 1. files 테이블 - 업로드된 파일 정보
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_records INTEGER NOT NULL,
        column_count INTEGER NOT NULL,
        uid_columns TEXT,  -- JSON array
        opinion_columns TEXT,  -- JSON array
        quantitative_columns TEXT,  -- JSON array
        file_path TEXT,
        file_data BLOB,  -- 실제 파일 데이터 (작은 파일용)
        status TEXT DEFAULT 'uploaded',
        metadata TEXT  -- JSON
    )
    """)
    print("✅ files 테이블 생성")
    
    # 2. jobs 테이블 - 분석 작업
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        sample_size INTEGER,
        analysis_mode TEXT DEFAULT 'hybrid',
        enable_ai_feedback BOOLEAN DEFAULT 0,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME,
        progress REAL DEFAULT 0.0,
        current INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        results_count INTEGER DEFAULT 0,
        error TEXT,
        config TEXT,  -- JSON 설정
        FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
    )
    """)
    print("✅ jobs 테이블 생성")
    
    # 3. results 테이블 - 분석 결과
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        overall_score REAL,
        grade TEXT,
        percentile REAL,
        text_score REAL,
        quantitative_score REAL,
        confidence REAL,
        dimension_scores TEXT,  -- JSON
        analysis_data TEXT,  -- JSON (전체 분석 데이터)
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
    )
    """)
    print("✅ results 테이블 생성")
    
    # 4. 인덱스 생성 (성능 최적화)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_upload_time ON files(upload_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_file_id ON jobs(file_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_job_id ON results(job_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_uid ON results(uid)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_grade ON results(grade)")
    print("✅ 인덱스 생성 완료")
    
    # 커밋
    conn.commit()
    
    # 검증
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("\n📊 생성된 테이블:")
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"\n  📋 {table[0]} 테이블:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
    
    conn.close()
    
    # 최종 확인
    file_size = os.path.getsize(db_path) / 1024
    print(f"\n✅ 데이터베이스 생성 완료!")
    print(f"   파일: {os.path.abspath(db_path)}")
    print(f"   크기: {file_size:.2f} KB")

if __name__ == "__main__":
    init_database()