#!/usr/bin/env python3
"""
AIRISS v4 AWS Elastic Beanstalk 배포용 ZIP 파일 생성
"""

import zipfile
import os
import shutil
from datetime import datetime

def create_deployment_zip():
    """배포용 ZIP 파일 생성"""
    
    # 제외할 폴더/파일 목록
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.github',
        'venv',
        'node_modules',
        'logs',
        'temp_data',
        'uploads',
        'test_results',
        'backup_archive',
        '.env',
        'airiss.db',
        '*.pyc',
        '*.log',
        '.gitignore',
        'README.md',
        'debug_logs',
        'test_data'
    ]
    
    # ZIP 파일명 (타임스탬프 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"airiss_v4_deployment_{timestamp}.zip"
    
    print(f"🚀 AIRISS v4 배포용 ZIP 파일 생성 중...")
    print(f"📦 파일명: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # 현재 디렉토리의 모든 파일 추가
        for root, dirs, files in os.walk('.'):
            # 제외할 디렉토리 필터링
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                # 제외할 파일 필터링
                if any(pattern in file for pattern in exclude_patterns):
                    continue
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                # ZIP 내부 경로 (상대 경로)
                arcname = os.path.relpath(file_path, '.')
                
                zipf.write(file_path, arcname)
                print(f"  ✅ {arcname}")
    
    file_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
    print(f"\n✅ ZIP 파일 생성 완료!")
    print(f"📦 파일: {zip_filename}")
    print(f"💾 크기: {file_size:.1f} MB")
    print(f"\n📋 다음 단계:")
    print(f"1. AWS Console → Elastic Beanstalk")
    print(f"2. 'Create Application' 클릭")
    print(f"3. '{zip_filename}' 업로드")
    print(f"4. 배포 완료!")
    
    return zip_filename

if __name__ == "__main__":
    create_deployment_zip()
