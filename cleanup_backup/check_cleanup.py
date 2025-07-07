#!/usr/bin/env python3
"""
AIRISS v4 정리 사전 점검 스크립트
실제 정리 전에 어떤 파일들이 정리될지 미리 확인
"""

import os
import glob

def check_cleanup_targets():
    """정리 대상 파일들 확인"""
    
    print("🔍 AIRISS v4 정리 대상 파일 점검")
    print("=" * 50)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 정리 대상 패턴들
    patterns = {
        "백업 파일": ["*_backup*", "*_fixed*", "*_emergency*", "*_enhanced*"],
        "임시 파일": ["*_debug*", "*_temp*", "*_old*", "*_test*"],
        "ZIP 파일": ["*.zip"],
        "배치 파일": ["*.bat", "*.ps1", "*.sh"],
        "중복 파일": ["application_*.py", "main_*.py", "Procfile_*"]
    }
    
    total_files = 0
    total_size = 0
    
    for category, pattern_list in patterns.items():
        print(f"\n📂 {category}:")
        category_files = []
        
        for pattern in pattern_list:
            matching_files = glob.glob(os.path.join(base_dir, pattern))
            for file_path in matching_files:
                if should_keep_file(os.path.basename(file_path)):
                    continue
                
                try:
                    file_size = os.path.getsize(file_path)
                    category_files.append((os.path.basename(file_path), file_size))
                    total_size += file_size
                except:
                    pass
        
        if category_files:
            for filename, size in sorted(category_files):
                size_mb = size / (1024 * 1024)
                print(f"  - {filename} ({size_mb:.1f}MB)")
            total_files += len(category_files)
        else:
            print("  (없음)")
    
    print(f"\n📊 정리 요약:")
    print(f"   총 파일 수: {total_files}개")
    print(f"   총 크기: {total_size / (1024 * 1024):.1f}MB")
    
    # 유지될 핵심 파일들
    print(f"\n✅ 유지될 핵심 파일들:")
    keep_files = [
        "requirements.txt", "README.md", "main.py", 
        "application.py", "Dockerfile", ".env.example"
    ]
    
    for filename in keep_files:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (없음)")
    
    # 핵심 폴더들
    print(f"\n📁 유지될 핵심 폴더들:")
    keep_dirs = ["app", "airiss-v4-frontend", "alembic", "docs", "scripts", "tests"]
    
    for dirname in keep_dirs:
        dir_path = os.path.join(base_dir, dirname)
        if os.path.exists(dir_path):
            print(f"  ✓ {dirname}/")
        else:
            print(f"  ✗ {dirname}/ (없음)")

def should_keep_file(filename):
    """유지해야 할 파일인지 확인"""
    keep_files = [
        "requirements.txt", "README.md", "LICENSE", "Dockerfile", 
        "docker-compose.yml", ".env", ".env.example", ".gitignore",
        "main.py", "application.py", "Procfile", "runtime.txt",
        "alembic.ini", "CHANGELOG.md", "CONTRIBUTING.md"
    ]
    return filename in keep_files

if __name__ == "__main__":
    check_cleanup_targets()
    
    print(f"\n" + "=" * 50)
    print("💡 이 점검 결과를 확인한 후:")
    print("   1. CLEANUP_SIMPLE.bat 실행")
    print("   2. 또는 python cleanup_airiss_v4.py 실행")
    print("=" * 50)
