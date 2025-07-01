#!/usr/bin/env python3
"""
AIRISS 프로젝트 안전한 정리 스크립트 v2
- 에러 처리 강화
- 사용 중인 파일 건너뛰기
- 진행 상황 상세 표시
"""

import os
import shutil
from pathlib import Path
import time

def safe_cleanup_airiss():
    """안전한 AIRISS 프로젝트 정리"""
    
    root_dir = Path(".")
    backup_dir = root_dir / "backup_archive"
    
    # 보존할 핵심 파일/폴더들
    keep_items = {
        "app",                    # 메인 애플리케이션
        "requirements.txt",       # 의존성
        ".env",                  # 환경설정
        ".env.example",          # 환경설정 예시
        "alembic",              # DB 마이그레이션
        "alembic.ini",          # alembic 설정
        "airiss.db",            # 데이터베이스
        "README.md",            # 프로젝트 설명
        ".git",                 # Git 저장소
        ".gitignore",           # Git 무시 파일
        "backup_archive",       # 백업 폴더
        "venv",                 # 가상환경
        "cleanup_project.py",   # 기존 스크립트
        "safe_cleanup.py"       # 이 스크립트
    }
    
    print("🧹 AIRISS 프로젝트 안전한 정리 시작...")
    print(f"📁 백업 폴더: {backup_dir}")
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    
    # 배치 파일들 우선 처리
    print("\n🔧 1단계: 배치 파일(.bat) 정리...")
    bat_files = list(root_dir.glob("*.bat"))
    for bat_file in bat_files:
        if safe_move_file(bat_file, backup_dir / "scripts", "배치파일"):
            moved_count += 1
        else:
            error_count += 1
    
    # 테스트 파일들 처리
    print("\n🧪 2단계: 테스트 파일 정리...")
    test_patterns = ["test_*.py", "debug_*.py", "diagnose_*.py", "check_*.py", "quick_*.py"]
    for pattern in test_patterns:
        for test_file in root_dir.glob(pattern):
            if test_file.name not in keep_items:
                if safe_move_file(test_file, backup_dir / "test_files", "테스트"):
                    moved_count += 1
                else:
                    error_count += 1
    
    # PowerShell 스크립트 처리
    print("\n⚡ 3단계: PowerShell 스크립트(.ps1) 정리...")
    ps1_files = list(root_dir.glob("*.ps1"))
    for ps1_file in ps1_files:
        if safe_move_file(ps1_file, backup_dir / "scripts", "PS스크립트"):
            moved_count += 1
        else:
            error_count += 1
    
    # 가이드 문서들 처리
    print("\n📚 4단계: 가이드 문서 정리...")
    guide_patterns = ["*_GUIDE*.md", "*_CHECKLIST*.md", "COMMERCIALIZATION*.md", "ULTIMATE*.md"]
    for pattern in guide_patterns:
        for guide_file in root_dir.glob(pattern):
            if guide_file.name not in keep_items:
                if safe_move_file(guide_file, backup_dir / "docs", "문서"):
                    moved_count += 1
                else:
                    error_count += 1
    
    # 설정 및 스크립트 파일들
    print("\n⚙️ 5단계: 설정/스크립트 파일 정리...")
    script_patterns = ["apply_*.py", "fix_*.py", "update_*.py", "restore_*.py", "deploy*"]
    for pattern in script_patterns:
        for script_file in root_dir.glob(pattern):
            if script_file.name not in keep_items:
                if safe_move_file(script_file, backup_dir / "fix_files", "스크립트"):
                    moved_count += 1
                else:
                    error_count += 1
    
    # 로그 및 임시 파일들
    print("\n📊 6단계: 로그/임시 파일 정리...")
    temp_patterns = ["*.log", "*.json", "diagnosis*", "diagnostic*"]
    for pattern in temp_patterns:
        for temp_file in root_dir.glob(pattern):
            if temp_file.name not in keep_items:
                if safe_move_file(temp_file, backup_dir / "temp", "임시파일"):
                    moved_count += 1
                else:
                    error_count += 1
    
    # 백업 파일들
    print("\n💾 7단계: 백업 파일 정리...")
    backup_patterns = ["*backup*", "*_old.*"]
    for pattern in backup_patterns:
        for backup_file in root_dir.glob(pattern):
            if backup_file.name not in keep_items and "backup_archive" not in str(backup_file):
                if safe_move_file(backup_file, backup_dir / "backup_files", "백업파일"):
                    moved_count += 1
                else:
                    error_count += 1
    
    # 나머지 기타 파일들
    print("\n🗂️ 8단계: 기타 파일 정리...")
    for item in root_dir.iterdir():
        if (item.name not in keep_items and 
            not item.name.startswith('.') and 
            item.is_file() and
            not item.name.endswith('.py')):  # 중요한 .py 파일은 건드리지 않음
            
            if safe_move_file(item, backup_dir / "misc", "기타"):
                moved_count += 1
            else:
                error_count += 1
    
    print(f"\n✅ 정리 완료!")
    print(f"📦 이동된 파일: {moved_count}개")
    print(f"⚠️ 건너뛴 파일: {skipped_count}개")
    print(f"❌ 에러 발생: {error_count}개")
    
    # 최종 상태 확인
    print("\n📋 남은 파일/폴더:")
    remaining_items = sorted([item.name for item in root_dir.iterdir() 
                            if not item.name.startswith('.')])
    for item in remaining_items:
        print(f"  ✅ {item}")

def safe_move_file(source_path, target_dir, file_type):
    """안전한 파일 이동 (에러 처리 포함)"""
    try:
        # 대상 디렉토리가 없으면 생성
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source_path.name
        
        # 이미 존재하는 파일이면 건너뛰기
        if target_path.exists():
            print(f"⚠️ 건너뛰기: {source_path.name} (이미 존재)")
            return False
        
        # 파일 이동
        shutil.move(str(source_path), str(target_path))
        print(f"📦 이동: {source_path.name} → {target_dir.name}/ ({file_type})")
        
        # 잠시 대기 (파일 시스템 동기화)
        time.sleep(0.1)
        return True
        
    except PermissionError:
        print(f"⚠️ 권한 오류: {source_path.name} (사용 중인 파일)")
        return False
    except FileNotFoundError:
        print(f"⚠️ 파일 없음: {source_path.name}")
        return False
    except Exception as e:
        print(f"❌ 이동 실패: {source_path.name} - {e}")
        return False

if __name__ == "__main__":
    safe_cleanup_airiss()
