# fix_init_files.py
import os

# 프로젝트 구조와 __init__.py 내용
init_files = {
    "app": '"""AIRISS v4.0 - OK금융그룹 AI 기반 인재 스코어링 시스템"""\n__version__ = "4.0.0"\n',
    "app/api": '"""API 라우터 모듈"""\n',
    "app/core": '"""핵심 분석 엔진 모듈"""\n',
    "app/services": '"""비즈니스 서비스 모듈"""\n',
    "app/db": '"""데이터베이스 모듈"""\n',
    "app/schemas": '"""Pydantic 스키마 모듈"""\n'
}

# 디렉토리 생성 및 __init__.py 파일 생성
for path, content in init_files.items():
    # 디렉토리가 없으면 생성
    if not os.path.exists(path):
        os.makedirs(path)
    
    # __init__.py 파일 경로
    init_file = os.path.join(path, "__init__.py")
    
    # UTF-8 인코딩으로 파일 작성
    with open(init_file, 'w', encoding='utf-8', newline='') as f:
        f.write(content)
    
    print(f"✅ {init_file} 생성 완료")

print("\n모든 __init__.py 파일이 정상적으로 생성되었습니다!")