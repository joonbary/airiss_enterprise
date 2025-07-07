#!/usr/bin/env python3
"""
AIRISS v4 프로젝트 정리 스크립트
React 프론트엔드 기반의 최종 버전만 남기고 불필요한 파일들 정리
"""

import os
import shutil
import glob
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 현재 스크립트 실행 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, "cleanup_backup")

def create_backup_with_timestamp():
    """정리 전 전체 백업 생성"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"airiss_v4_before_cleanup_{timestamp}"
    backup_path = os.path.join(os.path.dirname(BASE_DIR), backup_name)
    
    logger.info(f"🔄 전체 백업 생성 중: {backup_path}")
    
    # 현재 폴더를 상위 폴더에 백업
    shutil.copytree(BASE_DIR, backup_path, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', 'node_modules', '.git', 'venv', '*.log'
    ))
    
    logger.info(f"✅ 백업 완료: {backup_path}")
    return backup_path

def move_to_cleanup_backup(file_path):
    """파일을 cleanup_backup 폴더로 이동"""
    if os.path.exists(file_path):
        try:
            rel_path = os.path.relpath(file_path, BASE_DIR)
            backup_file_path = os.path.join(BACKUP_DIR, rel_path)
            
            # 백업 폴더의 하위 디렉토리 생성
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            
            if os.path.isdir(file_path):
                shutil.move(file_path, backup_file_path)
            else:
                shutil.move(file_path, backup_file_path)
            
            logger.info(f"📦 이동: {rel_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 이동 실패 {file_path}: {e}")
            return False
    return False

def cleanup_files():
    """불필요한 파일들 정리"""
    
    # 1. 백업 및 임시 파일 패턴들
    backup_patterns = [
        "*_backup*", "*_fixed*", "*_emergency*", "*_enhanced*", 
        "*_stable*", "*_minimal*", "*_debug*", "*_phase*",
        "*_hotfix*", "*_simple*", "*_alt*", "*_old*"
    ]
    
    # 2. ZIP 파일들
    zip_patterns = ["*.zip"]
    
    # 3. 배치 파일들 (핵심 배포 스크립트 제외)
    bat_patterns = [
        "*.bat", "*.ps1", "*.sh"
    ]
    
    # 4. 임시 폴더들
    temp_folders = [
        "backup_archive", "debug_logs", "temp_data", "temp_deployment",
        "test_results", "test_server", "fixed_files", "fixed_scripts",
        "phase2_deployment", "logs"
    ]
    
    # 5. 중복 파일들
    duplicate_files = [
        "application_*.py", "main_*.py", "Procfile_*", "requirements_*.txt",
        "*_guide.md", "*_fix.py", "*_test.py", "deploy_*.py", "create_*.py",
        "check_*.py", "fix_*.py", "setup_*.py", "monitor_*.py",
        "emergency_*.py", "run_*.py", "test_*.py"
    ]
    
    logger.info("🧹 파일 정리 시작...")
    
    # 패턴 기반 파일 정리
    all_patterns = backup_patterns + zip_patterns + bat_patterns + duplicate_files
    
    for pattern in all_patterns:
        matching_files = glob.glob(os.path.join(BASE_DIR, pattern))
        for file_path in matching_files:
            # 핵심 파일들은 보호
            file_name = os.path.basename(file_path)
            if should_keep_file(file_name):
                continue
            
            move_to_cleanup_backup(file_path)
    
    # 임시 폴더들 정리
    for folder in temp_folders:
        folder_path = os.path.join(BASE_DIR, folder)
        if os.path.exists(folder_path):
            move_to_cleanup_backup(folder_path)
    
    # app 폴더 내 백업 파일들 정리
    cleanup_app_folder()

def should_keep_file(filename):
    """유지해야 할 핵심 파일인지 확인"""
    keep_files = [
        "requirements.txt", "README.md", "LICENSE", "Dockerfile", 
        "docker-compose.yml", ".env", ".env.example", ".gitignore",
        "main.py", "application.py", "Procfile", "runtime.txt",
        "alembic.ini", "CHANGELOG.md", "CONTRIBUTING.md"
    ]
    
    return filename in keep_files

def cleanup_app_folder():
    """app 폴더 내 백업 파일들 정리"""
    app_folder = os.path.join(BASE_DIR, "app")
    if not os.path.exists(app_folder):
        return
    
    logger.info("🧹 app 폴더 정리 중...")
    
    # app 폴더 내 백업 파일들
    backup_files = glob.glob(os.path.join(app_folder, "*_backup*"))
    backup_files.extend(glob.glob(os.path.join(app_folder, "*_enhanced*")))
    backup_files.extend(glob.glob(os.path.join(app_folder, "*_fixed*")))
    backup_files.extend(glob.glob(os.path.join(app_folder, "*_optimized*")))
    backup_files.extend(glob.glob(os.path.join(app_folder, "*_pwa*")))
    
    for backup_file in backup_files:
        if os.path.basename(backup_file) != "main.py":  # main.py는 유지
            move_to_cleanup_backup(backup_file)

def cleanup_pycache():
    """__pycache__ 폴더들 정리"""
    logger.info("🧹 __pycache__ 폴더 정리 중...")
    
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                logger.info(f"🗑️ 삭제: {os.path.relpath(pycache_path, BASE_DIR)}")
            except Exception as e:
                logger.error(f"❌ __pycache__ 삭제 실패: {e}")

def create_clean_structure_summary():
    """정리 후 구조 요약 생성"""
    summary_file = os.path.join(BASE_DIR, "PROJECT_STRUCTURE_CLEAN.md")
    
    structure = []
    structure.append("# AIRISS v4 정리된 프로젝트 구조\n")
    structure.append(f"정리 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    structure.append("## 핵심 디렉토리\n")
    
    # 핵심 디렉토리들
    core_dirs = ["app", "airiss-v4-frontend", "alembic", "static", "docs", "scripts", "tests"]
    
    for dir_name in core_dirs:
        dir_path = os.path.join(BASE_DIR, dir_name)
        if os.path.exists(dir_path):
            structure.append(f"### {dir_name}/\n")
            try:
                for item in sorted(os.listdir(dir_path)):
                    if not item.startswith('.') and not item.startswith('__'):
                        item_path = os.path.join(dir_path, item)
                        if os.path.isdir(item_path):
                            structure.append(f"- {item}/\n")
                        else:
                            structure.append(f"- {item}\n")
            except PermissionError:
                structure.append("- (접근 권한 없음)\n")
            structure.append("\n")
    
    structure.append("## 핵심 파일\n")
    core_files = [
        "main.py", "application.py", "requirements.txt", "README.md",
        "Dockerfile", "docker-compose.yml", ".env.example"
    ]
    
    for file_name in core_files:
        file_path = os.path.join(BASE_DIR, file_name)
        if os.path.exists(file_path):
            structure.append(f"- ✅ {file_name}\n")
        else:
            structure.append(f"- ❌ {file_name} (없음)\n")
    
    structure.append(f"\n## 정리된 파일들\n")
    structure.append(f"정리된 파일들은 `cleanup_backup/` 폴더에 보관되어 있습니다.\n")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.writelines(structure)
    
    logger.info(f"📋 구조 요약 생성: {summary_file}")

def main():
    """메인 실행 함수"""
    logger.info("🎯 AIRISS v4 프로젝트 정리 시작")
    logger.info("=" * 60)
    
    try:
        # 1. 전체 백업 생성
        backup_path = create_backup_with_timestamp()
        
        # 2. 파일 정리
        cleanup_files()
        
        # 3. __pycache__ 정리
        cleanup_pycache()
        
        # 4. 정리된 구조 요약 생성
        create_clean_structure_summary()
        
        logger.info("=" * 60)
        logger.info("✅ AIRISS v4 프로젝트 정리 완료!")
        logger.info(f"📦 전체 백업: {backup_path}")
        logger.info(f"🧹 정리된 파일들: {BACKUP_DIR}")
        logger.info("📋 프로젝트 구조: PROJECT_STRUCTURE_CLEAN.md")
        
        # 남은 핵심 구조 출력
        logger.info("\n🎯 정리 후 핵심 구조:")
        logger.info("├── app/                 (백엔드 API)")
        logger.info("├── airiss-v4-frontend/  (React 프론트엔드)")
        logger.info("├── requirements.txt     (의존성)")
        logger.info("├── README.md           (문서)")
        logger.info("├── Dockerfile          (컨테이너)")
        logger.info("└── .env.example        (환경설정 예시)")
        
    except Exception as e:
        logger.error(f"❌ 정리 중 오류 발생: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
