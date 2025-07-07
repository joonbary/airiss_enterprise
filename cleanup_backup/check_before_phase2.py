#!/usr/bin/env python3
"""
AIRISS Phase 2 실행 전 종합 점검 스크립트
"""

import sys
import os
import importlib.util

def check_python_version():
    """Python 버전 확인"""
    print("🐍 Python 버전 확인...")
    version = sys.version_info
    print(f"   현재 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python 버전 OK")
        return True
    else:
        print("   ❌ Python 3.8+ 필요")
        return False

def check_required_modules():
    """필수 모듈 확인"""
    print("\n📦 필수 모듈 확인...")
    
    required_modules = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'numpy',
        'sqlite3',
        'logging',
        'typing',
        'datetime'
    ]
    
    all_ok = True
    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            else:
                spec = importlib.util.find_spec(module)
                if spec is None:
                    raise ImportError(f"Module {module} not found")
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (누락)")
            all_ok = False
    
    return all_ok

def check_airiss_modules():
    """AIRISS 모듈 확인"""
    print("\n🧠 AIRISS 모듈 확인...")
    
    # Change to airiss directory
    airiss_path = os.path.join(os.getcwd(), 'app')
    if airiss_path not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    airiss_modules = [
        ('app.services.text_analyzer', 'AIRISSTextAnalyzer'),
        ('app.services.quantitative_analyzer', 'QuantitativeAnalyzer'),
        ('app.services.hybrid_analyzer', 'AIRISSHybridAnalyzer'),
        ('app.db.sqlite_service', 'SQLiteService')
    ]
    
    all_ok = True
    for module_name, class_name in airiss_modules:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"   ❌ {module_name}.{class_name} - {e}")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """파일 구조 확인"""
    print("\n📁 파일 구조 확인...")
    
    required_files = [
        'application_phase2_preparation.py',
        'app/services/text_analyzer.py',
        'app/services/quantitative_analyzer.py', 
        'app/services/hybrid_analyzer.py',
        'app/db/sqlite_service.py',
        'app/templates',
        'app/static'
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (누락)")
            if file_path.endswith(('.py')):
                all_ok = False
    
    return all_ok

def main():
    """메인 점검 함수"""
    print("=" * 60)
    print("🔍 AIRISS Phase 2 실행 전 종합 점검")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_required_modules(),
        check_file_structure(),
        check_airiss_modules()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("🎉 모든 점검 통과! Phase 2 실행 준비 완료!")
        print("\n다음 명령어로 실행하세요:")
        print("   python application_phase2_preparation.py")
        print("\n또는 배치 파일 실행:")
        print("   EXECUTE_PHASE2_NOW.bat")
        print("\n서버 시작 후 접속:")
        print("   🌐 http://localhost:8000")
        print("   📊 http://localhost:8000/status")
        return True
    else:
        print("❌ 일부 점검 실패. 위의 오류를 확인하세요.")
        print("\n해결 방법:")
        print("1. 누락된 모듈 설치: pip install fastapi uvicorn pandas numpy")
        print("2. 파일 경로 확인")
        print("3. Python 버전 업그레이드 (3.8+)")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nEnter 키를 눌러 종료...")
