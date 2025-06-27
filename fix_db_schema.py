# fix_db_schema.py
# AIRISS v4.0 데이터베이스 스키마 문제 완전 해결 스크립트

import os
import sqlite3
import asyncio
from datetime import datetime
import shutil

class DatabaseFixer:
    def __init__(self):
        self.db_files = ["airiss.db", "airiss_v4.db"]
        
    def print_status(self, message, status="INFO"):
        """상태 메시지 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "SUCCESS": "✅",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        symbol = symbols.get(status, "ℹ️")
        print(f"{symbol} [{timestamp}] {message}")
    
    def backup_existing_databases(self):
        """기존 데이터베이스 백업"""
        self.print_status("기존 데이터베이스 백업 중...")
        
        backup_count = 0
        for db_file in self.db_files:
            if os.path.exists(db_file):
                backup_name = f"{db_file}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    shutil.copy2(db_file, backup_name)
                    self.print_status(f"백업 완료: {backup_name}", "SUCCESS")
                    backup_count += 1
                except Exception as e:
                    self.print_status(f"백업 실패 {db_file}: {e}", "ERROR")
        
        if backup_count > 0:
            self.print_status(f"{backup_count}개 데이터베이스 백업 완료", "SUCCESS")
        else:
            self.print_status("백업할 데이터베이스가 없습니다", "INFO")
    
    def remove_old_databases(self):
        """기존 데이터베이스 삭제"""
        self.print_status("기존 데이터베이스 파일 제거 중...")
        
        removed_count = 0
        for db_file in self.db_files:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    self.print_status(f"삭제 완료: {db_file}", "SUCCESS")
                    removed_count += 1
                except Exception as e:
                    self.print_status(f"삭제 실패 {db_file}: {e}", "ERROR")
        
        if removed_count > 0:
            self.print_status(f"{removed_count}개 파일 삭제 완료", "SUCCESS")
        else:
            self.print_status("삭제할 파일이 없습니다", "INFO")
    
    async def create_new_database(self):
        """SQLiteService를 사용하여 새 데이터베이스 생성"""
        self.print_status("새 데이터베이스 생성 중...")
        
        try:
            from app.db.sqlite_service import SQLiteService
            service = SQLiteService("airiss.db")
            await service.init_database()
            self.print_status("새 데이터베이스 생성 완료", "SUCCESS")
            return True
        except Exception as e:
            self.print_status(f"데이터베이스 생성 실패: {e}", "ERROR")
            return False
    
    def verify_database_schema(self):
        """데이터베이스 스키마 검증"""
        self.print_status("데이터베이스 스키마 검증 중...")
        
        if not os.path.exists("airiss.db"):
            self.print_status("airiss.db 파일이 존재하지 않습니다", "ERROR")
            return False
        
        try:
            conn = sqlite3.connect("airiss.db")
            cursor = conn.cursor()
            
            # files 테이블 스키마 확인
            cursor.execute("PRAGMA table_info(files);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['id', 'filename', 'upload_time', 'total_records', 
                              'columns', 'uid_columns', 'opinion_columns', 
                              'quantitative_columns', 'file_data']
            
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                self.print_status(f"누락된 컬럼: {missing_columns}", "ERROR")
                return False
            else:
                self.print_status("모든 필수 컬럼이 정상적으로 생성됨", "SUCCESS")
                
            # 테이블 목록 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            
            required_tables = ['files', 'jobs', 'results']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.print_status(f"누락된 테이블: {missing_tables}", "ERROR")
                return False
            else:
                self.print_status("모든 필수 테이블이 정상적으로 생성됨", "SUCCESS")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_status(f"스키마 검증 실패: {e}", "ERROR")
            return False
    
    async def run_complete_fix(self):
        """완전한 데이터베이스 문제 해결"""
        print("🔧 AIRISS v4.0 데이터베이스 스키마 완전 수정")
        print("=" * 60)
        
        # 1. 백업
        self.backup_existing_databases()
        
        # 2. 기존 파일 삭제
        self.remove_old_databases()
        
        # 3. 새 데이터베이스 생성
        success = await self.create_new_database()
        if not success:
            self.print_status("데이터베이스 생성 실패로 작업 중단", "ERROR")
            return False
        
        # 4. 스키마 검증
        if self.verify_database_schema():
            print("\n" + "=" * 60)
            self.print_status("🎉 데이터베이스 문제 완전 해결!", "SUCCESS")
            self.print_status("이제 python test_airiss_v4.py를 실행하세요", "INFO")
            return True
        else:
            self.print_status("스키마 검증 실패", "ERROR")
            return False

async def main():
    fixer = DatabaseFixer()
    await fixer.run_complete_fix()

if __name__ == "__main__":
    asyncio.run(main())
