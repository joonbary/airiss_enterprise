# quick_test_imports.py
# 핵심 모듈들 import 테스트

import sys
import traceback
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def test_import(module_name, import_statement):
    """모듈 import 테스트"""
    try:
        exec(import_statement)
        print(f"{Colors.GREEN}✅ {module_name}: 정상{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ {module_name}: {e}{Colors.END}")
        print(f"   상세: {traceback.format_exc()}")
        return False

def main():
    print(f"{Colors.YELLOW}🔍 AIRISS v4.0 핵심 모듈 Import 테스트{Colors.END}")
    print("=" * 60)
    
    # 테스트할 import들
    imports = [
        ("FastAPI", "from fastapi import FastAPI"),
        ("SQLiteService", "from app.db.sqlite_service import SQLiteService"),
        ("ConnectionManager", "from app.core.websocket_manager import ConnectionManager"),
        ("Analysis Router", "from app.api.analysis import router"),
        ("Upload Router", "from app.api.upload import router as upload_router"),
        ("Main App", "from app.main import app")
    ]
    
    success_count = 0
    
    for module_name, import_statement in imports:
        if test_import(module_name, import_statement):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"결과: {success_count}/{len(imports)} 성공")
    
    if success_count == len(imports):
        print(f"{Colors.GREEN}🎉 모든 import 성공! main.py 문제일 가능성{Colors.END}")
        print(f"{Colors.YELLOW}📋 main.py의 startup 이벤트에서 문제 발생 추정{Colors.END}")
    else:
        print(f"{Colors.RED}❌ Import 문제 발견! 해당 모듈 수정 필요{Colors.END}")

if __name__ == "__main__":
    main()
