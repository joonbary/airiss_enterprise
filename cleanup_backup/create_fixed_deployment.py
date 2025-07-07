#!/usr/bin/env python3
"""
AIRISS v4 - AWS Elastic Beanstalk 재배포 패키지 생성
오류 수정된 버전으로 새 배포 패키지 생성
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_fixed_deployment_package():
    """수정된 설정으로 새 배포 패키지 생성"""
    
    # 현재 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 배포 패키지 이름
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"airiss_v4_fixed_{timestamp}.zip"
    
    # 포함할 파일/폴더 목록
    include_items = [
        'app/',
        'static/',
        'templates/',
        '.ebextensions/',
        'application.py',
        'requirements.txt',
        'Procfile',          # 새로 추가
        'runtime.txt',       # 새로 추가
        'init_database.py',
        'create_db_files.py',
        'alembic.ini',
        'alembic/',
        '.env.example'
    ]
    
    # 제외할 항목들
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.pytest_cache',
        'venv',
        'node_modules',
        '*.log',
        '*.db',
        'uploads/',
        'test_data/',
        'debug_logs/',
        'backup_archive/'
    ]
    
    print(f"🔧 AIRISS v4 수정된 배포 패키지 생성 시작...")
    
    # ZIP 파일 생성
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in include_items:
            item_path = os.path.join(current_dir, item)
            
            if os.path.isfile(item_path):
                # 파일 추가
                zipf.write(item_path, item)
                print(f"✅ 파일 추가: {item}")
                
            elif os.path.isdir(item_path):
                # 디렉토리 추가
                for root, dirs, files in os.walk(item_path):
                    # 제외 패턴 필터링
                    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                    
                    for file in files:
                        if not any(pattern in file for pattern in exclude_patterns):
                            file_path = os.path.join(root, file)
                            arc_path = os.path.relpath(file_path, current_dir)
                            zipf.write(file_path, arc_path)
                
                print(f"✅ 디렉토리 추가: {item}")
            else:
                print(f"⚠️ 항목 없음: {item}")
    
    print(f"\n🎉 배포 패키지 생성 완료: {package_name}")
    print(f"📁 파일 크기: {os.path.getsize(package_name) / (1024*1024):.1f} MB")
    
    return package_name

if __name__ == "__main__":
    package_file = create_fixed_deployment_package()
    
    print(f"\n🚀 다음 단계:")
    print(f"1. AWS Elastic Beanstalk 콘솔에서 '업로드 및 배포' 클릭")
    print(f"2. 생성된 파일 선택: {package_file}")
    print(f"3. 버전 레이블: AIRISS-v4-Fixed-{datetime.now().strftime('%Y%m%d')}")
    print(f"4. 배포 실행")
