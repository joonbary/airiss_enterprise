# debug_file_issue.py
import requests
import sqlite3
import os
import json

BASE_URL = "http://localhost:8002"

def check_database():
    """데이터베이스 상태 확인"""
    print("🔍 데이터베이스 확인...")
    
    # 가능한 DB 파일 위치들
    db_paths = [
        "airiss.db",
        "app/airiss.db",
        "../airiss.db",
        "data/airiss.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ DB 파일 발견: {db_path}")
            
            # 테이블 확인
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 테이블 목록
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   테이블 목록: {[t[0] for t in tables]}")
            
            # files 테이블이 있다면 내용 확인
            if any('file' in t[0].lower() for t in tables):
                cursor.execute("SELECT * FROM files LIMIT 5;")
                files = cursor.fetchall()
                print(f"   파일 레코드 수: {len(files)}")
                
            conn.close()
            return db_path
    
    print("❌ 데이터베이스 파일을 찾을 수 없습니다!")
    return None

def check_upload_directory():
    """업로드 디렉토리 확인"""
    print("\n📁 업로드 디렉토리 확인...")
    
    upload_dirs = [
        "uploads",
        "app/uploads", 
        "temp",
        "app/temp",
        "data/uploads"
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 디렉토리 발견: {dir_path}")
            files = os.listdir(dir_path)
            print(f"   파일 수: {len(files)}")
            if files:
                print(f"   최근 파일: {files[-5:]}")  # 최근 5개

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n🌐 API 엔드포인트 확인...")
    
    # API 문서 확인
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        api_spec = response.json()
        paths = api_spec.get('paths', {})
        print("✅ 사용 가능한 엔드포인트:")
        for path, methods in paths.items():
            if 'analysis' in path or 'upload' in path:
                print(f"   {path}: {list(methods.keys())}")

def detailed_upload_test():
    """상세한 업로드 테스트"""
    print("\n📤 상세 업로드 테스트...")
    
    # 작은 테스트 파일 생성
    import pandas as pd
    test_df = pd.DataFrame({
        'UID': ['TEST001'],
        '평가의견': ['테스트 의견입니다.'],
        '점수': [85]
    })
    test_df.to_excel('test_small.xlsx', index=False)
    
    # 업로드
    with open('test_small.xlsx', 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/api/v1/analysis/upload",
            files=files
        )
    
    print(f"업로드 응답 코드: {response.status_code}")
    print(f"업로드 응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        file_id = response.json()['file_id']
        
        # 즉시 분석 시도
        print(f"\n분석 시도 (File ID: {file_id})...")
        analyze_response = requests.post(
            f"{BASE_URL}/api/v1/analysis/analyze/{file_id}",
            json={"sample_size": 1, "analysis_mode": "hybrid"}
        )
        print(f"분석 응답 코드: {analyze_response.status_code}")
        print(f"분석 응답: {analyze_response.text}")

if __name__ == "__main__":
    print("🔧 AIRISS v4.0 파일 시스템 디버깅")
    print("="*50)
    
    # 1. 데이터베이스 확인
    db_path = check_database()
    
    # 2. 업로드 디렉토리 확인
    check_upload_directory()
    
    # 3. API 엔드포인트 확인
    test_api_endpoints()
    
    # 4. 상세 업로드 테스트
    detailed_upload_test()