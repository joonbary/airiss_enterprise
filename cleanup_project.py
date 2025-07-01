#!/usr/bin/env python3
"""
AIRISS 프로젝트 자동 정리 스크립트
- main.py와 핵심 파일들만 남기고 나머지는 backup_archive로 이동
"""

import os
import shutil
from pathlib import Path

def cleanup_airiss_project():
    """AIRISS 프로젝트 정리"""
    
    # 현재 디렉토리
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
        "venv",                 # 가상환경 (있다면)
        "cleanup_project.py"    # 이 스크립트 자체
    }
    
    # 이동할 파일 카테고리 정의
    categories = {
        "scripts": [".bat", ".ps1", ".sh"],
        "test_files": ["test_", "debug_", "diagnose_", "check_", "quick_"],
        "backup_files": ["backup_", "_backup", ".db_backup"],
        "fix_files": ["fix_", "apply_", "update_", "restore_"],
        "docs": [".md", ".txt"],
        "temp": [".log", ".json", "temp_", "_temp"],
        "misc": []  # 기타
    }
    
    print("🧹 AIRISS 프로젝트 정리 시작...")
    print(f"📁 백업 폴더: {backup_dir}")
    
    moved_count = 0
    
    # 루트 디렉토리의 모든 파일/폴더 검사
    for item in root_dir.iterdir():
        # 숨겨진 파일이나 보존 대상은 건너뛰기
        if item.name.startswith('.') or item.name in keep_items:
            print(f"✅ 보존: {item.name}")
            continue
        
        # 카테고리 결정
        category = determine_category(item.name, categories)
        target_dir = backup_dir / category
        target_path = target_dir / item.name
        
        try:
            # 파일/폴더 이동
            if item.is_file():
                shutil.move(str(item), str(target_path))
                print(f"📦 이동: {item.name} → {category}/")
            elif item.is_dir():
                shutil.move(str(item), str(target_path))
                print(f"📁 이동: {item.name}/ → {category}/")
            
            moved_count += 1
            
        except Exception as e:
            print(f"❌ 이동 실패: {item.name} - {e}")
    
    print(f"\n✅ 정리 완료! {moved_count}개 항목을 백업 폴더로 이동했습니다.")
    print("\n📋 남은 핵심 파일들:")
    for item in sorted(keep_items):
        if (root_dir / item).exists():
            print(f"  - {item}")

def determine_category(filename, categories):
    """파일명을 기반으로 카테고리 결정"""
    filename_lower = filename.lower()
    
    # 각 카테고리별 패턴 검사
    for category, patterns in categories.items():
        for pattern in patterns:
            if pattern in filename_lower:
                return category
    
    # 특별 규칙들
    if any(x in filename_lower for x in ['.bat', '.ps1', '.sh']):
        return "scripts"
    elif any(x in filename_lower for x in ['.md', '.txt']) and 'readme' not in filename_lower:
        return "docs"
    elif any(x in filename_lower for x in ['.log', '.json']):
        return "temp"
    else:
        return "misc"

if __name__ == "__main__":
    cleanup_airiss_project()
