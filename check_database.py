# check_database.py
# AIRISS v4.0 SQLite 데이터베이스 상태 확인 스크립트

import sqlite3
import json
from datetime import datetime
import pandas as pd

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DatabaseChecker:
    def __init__(self, db_path: str = "airiss.db"):
        self.db_path = db_path
        
    def print_step(self, message: str, status: str = "INFO"):
        if status == "SUCCESS":
            color = Colors.GREEN
            symbol = "✅"
        elif status == "ERROR":
            color = Colors.RED
            symbol = "❌"
        elif status == "WARNING":
            color = Colors.YELLOW
            symbol = "⚠️"
        else:
            color = Colors.BLUE
            symbol = "ℹ️"
        
        print(f"{color}{symbol} {message}{Colors.END}")
    
    def check_database_exists(self):
        """데이터베이스 파일 존재 확인"""
        import os
        if os.path.exists(self.db_path):
            size = os.path.getsize(self.db_path)
            self.print_step(f"데이터베이스 파일 존재: {self.db_path} ({size} bytes)", "SUCCESS")
            return True
        else:
            self.print_step(f"데이터베이스 파일 없음: {self.db_path}", "ERROR")
            return False
    
    def check_tables(self):
        """테이블 구조 확인"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 테이블 목록 조회
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.print_step(f"발견된 테이블: {[table[0] for table in tables]}", "SUCCESS")
            
            expected_tables = ['files', 'jobs', 'results']
            for table_name in expected_tables:
                if any(table[0] == table_name for table in tables):
                    # 테이블 스키마 확인
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    schema = cursor.fetchall()
                    columns = [col[1] for col in schema]
                    self.print_step(f"{table_name} 테이블 컬럼: {columns}", "SUCCESS")
                else:
                    self.print_step(f"{table_name} 테이블 없음", "ERROR")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_step(f"테이블 확인 오류: {e}", "ERROR")
            return False
    
    def check_data_counts(self):
        """데이터 개수 확인"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 각 테이블의 레코드 수 확인
            tables = ['files', 'jobs', 'results']
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    count = cursor.fetchone()[0]
                    self.print_step(f"{table} 테이블 레코드 수: {count}개", "SUCCESS")
                except:
                    self.print_step(f"{table} 테이블 조회 실패", "ERROR")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_step(f"데이터 개수 확인 오류: {e}", "ERROR")
            return False
    
    def check_recent_jobs(self):
        """최근 작업 확인"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 최근 작업 5개 조회
            cursor.execute("""
                SELECT id, file_id, status, created_at, updated_at 
                FROM jobs 
                ORDER BY created_at DESC 
                LIMIT 5;
            """)
            
            jobs = cursor.fetchall()
            
            if jobs:
                self.print_step("최근 작업 목록:", "SUCCESS")
                for job in jobs:
                    job_id, file_id, status, created_at, updated_at = job
                    print(f"  📋 {job_id[:8]}... | {status} | {created_at}")
            else:
                self.print_step("저장된 작업이 없습니다", "WARNING")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_step(f"최근 작업 확인 오류: {e}", "ERROR")
            return False
    
    def check_job_id_consistency(self):
        """Job ID 일치성 확인"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # jobs 테이블에서 job_data 내부의 job_id와 테이블의 id 비교
            cursor.execute("SELECT id, job_data FROM jobs;")
            jobs = cursor.fetchall()
            
            inconsistent_count = 0
            
            for job in jobs:
                db_id = job[0]
                try:
                    job_data = json.loads(job[1])
                    data_job_id = job_data.get('job_id')
                    
                    if db_id != data_job_id:
                        inconsistent_count += 1
                        self.print_step(f"ID 불일치: DB={db_id[:8]}..., Data={data_job_id[:8] if data_job_id else 'None'}...", "ERROR")
                except:
                    self.print_step(f"job_data 파싱 실패: {db_id[:8]}...", "WARNING")
            
            if inconsistent_count == 0:
                self.print_step("모든 Job ID가 일치합니다", "SUCCESS")
            else:
                self.print_step(f"{inconsistent_count}개의 Job ID 불일치 발견", "ERROR")
            
            conn.close()
            return inconsistent_count == 0
            
        except Exception as e:
            self.print_step(f"Job ID 일치성 확인 오류: {e}", "ERROR")
            return False
    
    def run_check(self):
        """전체 데이터베이스 검사"""
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🗄️ AIRISS v4.0 SQLite 데이터베이스 상태 확인{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print()
        
        success_count = 0
        total_checks = 5
        
        # 1. 데이터베이스 파일 존재 확인
        if self.check_database_exists():
            success_count += 1
            
            # 2. 테이블 구조 확인
            if self.check_tables():
                success_count += 1
                
                # 3. 데이터 개수 확인
                if self.check_data_counts():
                    success_count += 1
                    
                    # 4. 최근 작업 확인
                    if self.check_recent_jobs():
                        success_count += 1
                        
                        # 5. Job ID 일치성 확인 (핵심)
                        if self.check_job_id_consistency():
                            success_count += 1
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        
        if success_count == total_checks:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 데이터베이스 상태 양호!{Colors.END}")
            print(f"{Colors.GREEN}✅ 모든 테이블 정상{Colors.END}")
            print(f"{Colors.GREEN}✅ Job ID 일치성 확인{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}⚠️ 데이터베이스 문제 발견 ({success_count}/{total_checks}){Colors.END}")
            
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")

def main():
    checker = DatabaseChecker()
    checker.run_check()

if __name__ == "__main__":
    main()
