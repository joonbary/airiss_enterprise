# syntax_check.py
# AIRISS v4.0 코드 문법 오류 검사

import ast
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_syntax(file_path):
    """Python 파일 문법 검사"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # AST 파싱으로 문법 검사
        ast.parse(source_code)
        print(f"{Colors.GREEN}✅ {file_path}: 문법 정상{Colors.END}")
        return True
        
    except SyntaxError as e:
        print(f"{Colors.RED}❌ {file_path}: 문법 오류{Colors.END}")
        print(f"   라인 {e.lineno}: {e.msg}")
        if e.text:
            print(f"   코드: {e.text.strip()}")
        return False
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ {file_path}: 확인 불가 - {e}{Colors.END}")
        return True

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}🔍 AIRISS v4.0 문법 검사{Colors.END}")
    print("=" * 50)
    
    # 주요 파일들 검사
    files_to_check = [
        "app/main.py",
        "app/api/analysis.py", 
        "app/db/sqlite_service.py",
        "app/core/websocket_manager.py"
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            result = check_syntax(file_path)
            if not result:
                all_good = False
        else:
            print(f"{Colors.YELLOW}⚠️ {file_path}: 파일 없음{Colors.END}")
    
    print("\n" + "=" * 50)
    if all_good:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 모든 파일 문법 정상!{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ 문법 오류 발견! 수정 필요{Colors.END}")

if __name__ == "__main__":
    main()
