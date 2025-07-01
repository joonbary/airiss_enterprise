#!/usr/bin/env python3
"""
AIRISS 로컬 자동 백업 스크립트
매일 실행하여 프로젝트를 안전하게 백업합니다.
"""

import os
import shutil
import datetime
import subprocess
import zipfile
import schedule
import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

class AIRISSBackup:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.backup_root = os.path.join(self.project_root, "backups")
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        """백업 디렉토리 생성"""
        os.makedirs(self.backup_root, exist_ok=True)
        
    def get_backup_filename(self):
        """백업 파일명 생성"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"airiss_backup_{timestamp}"
        
    def create_backup(self):
        """전체 백업 실행"""
        try:
            logging.info("🔄 AIRISS 백업 시작...")
            
            backup_name = self.get_backup_filename()
            backup_dir = os.path.join(self.backup_root, backup_name)
            os.makedirs(backup_dir, exist_ok=True)
            
            # 1. Git 정보 수집
            git_info = self.collect_git_info()
            
            # 2. 소스 코드 백업
            self.backup_source_code(backup_dir)
            
            # 3. 데이터베이스 백업
            self.backup_database(backup_dir)
            
            # 4. 설정 파일 백업
            self.backup_config_files(backup_dir)
            
            # 5. 백업 정보 파일 생성
            self.create_backup_info(backup_dir, git_info)
            
            # 6. 압축 파일 생성
            zip_file = self.create_zip_backup(backup_dir, backup_name)
            
            # 7. 임시 디렉토리 정리
            shutil.rmtree(backup_dir)
            
            # 8. 오래된 백업 정리
            self.cleanup_old_backups()
            
            logging.info(f"✅ 백업 완료: {zip_file}")
            return True
            
        except Exception as e:
            logging.error(f"❌ 백업 실패: {e}")
            return False
    
    def collect_git_info(self):
        """Git 정보 수집"""
        try:
            commit_hash = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], 
                cwd=self.project_root
            ).decode().strip()
            
            branch = subprocess.check_output(
                ['git', 'branch', '--show-current'], 
                cwd=self.project_root
            ).decode().strip()
            
            return {
                'commit': commit_hash,
                'branch': branch,
                'timestamp': datetime.datetime.now().isoformat()
            }
        except:
            return {'commit': 'unknown', 'branch': 'unknown'}
    
    def backup_source_code(self, backup_dir):
        """소스 코드 백업"""
        source_dir = os.path.join(backup_dir, "source")
        os.makedirs(source_dir, exist_ok=True)
        
        # 제외할 디렉토리/파일
        exclude_dirs = {
            '.git', '__pycache__', 'venv', 'node_modules', 
            'logs', 'temp_data', 'uploads', 'test_results',
            'backups'
        }
        
        exclude_files = {
            '.env', '*.pyc', '*.log', '*.tmp'
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # 제외 디렉토리 스킵
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            # 상대 경로 계산
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == '.':
                target_dir = source_dir
            else:
                target_dir = os.path.join(source_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
            
            # 파일 복사
            for file in files:
                if not any(file.endswith(ext.replace('*', '')) for ext in exclude_files):
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_dir, file)
                    shutil.copy2(src_file, dst_file)
        
        logging.info("📁 소스 코드 백업 완료")
    
    def backup_database(self, backup_dir):
        """데이터베이스 백업"""
        db_file = os.path.join(self.project_root, "airiss.db")
        if os.path.exists(db_file):
            db_backup_dir = os.path.join(backup_dir, "database")
            os.makedirs(db_backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_db_file = os.path.join(db_backup_dir, f"airiss_{timestamp}.db")
            shutil.copy2(db_file, backup_db_file)
            
            logging.info("💾 데이터베이스 백업 완료")
    
    def backup_config_files(self, backup_dir):
        """중요 설정 파일 백업"""
        config_dir = os.path.join(backup_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        config_files = [
            "requirements.txt",
            "docker-compose.yml", 
            "Dockerfile",
            ".env.example",
            "alembic.ini"
        ]
        
        for config_file in config_files:
            src_path = os.path.join(self.project_root, config_file)
            if os.path.exists(src_path):
                dst_path = os.path.join(config_dir, config_file)
                shutil.copy2(src_path, dst_path)
        
        logging.info("⚙️ 설정 파일 백업 완료")
    
    def create_backup_info(self, backup_dir, git_info):
        """백업 정보 파일 생성"""
        info_file = os.path.join(backup_dir, "backup_info.txt")
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("AIRISS 백업 정보\n")
            f.write("=" * 50 + "\n")
            f.write(f"백업 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Git 커밋: {git_info.get('commit', 'unknown')}\n")
            f.write(f"Git 브랜치: {git_info.get('branch', 'unknown')}\n")
            f.write("\n포함된 내용:\n")
            f.write("- 전체 소스 코드\n")
            f.write("- 데이터베이스 (airiss.db)\n")
            f.write("- 설정 파일들\n")
            f.write("- 문서 및 스크립트\n")
            f.write("\n제외된 내용:\n")
            f.write("- Git 히스토리\n")
            f.write("- Python 캐시 파일\n")
            f.write("- 로그 파일\n")
            f.write("- 임시 파일\n")
            f.write("- 업로드된 파일\n")
        
        logging.info("📋 백업 정보 파일 생성 완료")
    
    def create_zip_backup(self, backup_dir, backup_name):
        """압축 파일 생성"""
        zip_filename = f"{backup_name}.zip"
        zip_path = os.path.join(self.backup_root, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arc_name)
        
        # 파일 크기 확인
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        logging.info(f"📦 압축 파일 생성 완료: {zip_filename} ({size_mb:.1f}MB)")
        
        return zip_path
    
    def cleanup_old_backups(self, keep_days=30):
        """오래된 백업 파일 정리"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        
        deleted_count = 0
        for filename in os.listdir(self.backup_root):
            if filename.startswith("airiss_backup_") and filename.endswith(".zip"):
                file_path = os.path.join(self.backup_root, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
                    logging.info(f"🗑️ 오래된 백업 삭제: {filename}")
        
        if deleted_count > 0:
            logging.info(f"🧹 총 {deleted_count}개 파일 정리 완료")

def main():
    """메인 함수"""
    backup_manager = AIRISSBackup()
    
    # 즉시 백업 실행 (테스트용)
    print("🔄 AIRISS 백업 시스템 시작...")
    backup_manager.create_backup()
    
    # 스케줄 설정
    schedule.every().day.at("02:00").do(backup_manager.create_backup)  # 매일 오전 2시
    schedule.every().sunday.at("01:00").do(backup_manager.create_backup)  # 매주 일요일 추가
    
    print("⏰ 백업 스케줄 설정 완료:")
    print("   - 매일 오전 2시")
    print("   - 매주 일요일 오전 1시")
    print("   - Ctrl+C로 중지")
    
    # 스케줄 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        print("\n👋 백업 시스템 종료")

if __name__ == "__main__":
    main()
