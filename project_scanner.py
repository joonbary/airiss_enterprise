# project_scanner.py
import os
import json
from datetime import datetime
from pathlib import Path

def scan_project(root_dir="."):
    """프로젝트 구조와 파일 정보를 스캔"""
    project_info = {
        "scan_time": datetime.now().isoformat(),
        "root_directory": os.path.abspath(root_dir),
        "structure": {},
        "python_files": [],
        "other_files": [],
        "file_contents": {},
        "dependencies": set()
    }
    
    # 파일 트리 생성
    for root, dirs, files in os.walk(root_dir):
        # 제외할 디렉토리
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', 'env', '.env']]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        folder_name = os.path.basename(root)
        
        if folder_name:
            print(f"{indent}{folder_name}/")
            
        subindent = ' ' * 2 * (level + 1)
        
        for file in sorted(files):
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            
            print(f"{subindent}{file} ({file_size:,} bytes)")
            
            # Python 파일 분석
            if file.endswith('.py'):
                project_info["python_files"].append(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        project_info["file_contents"][file_path] = {
                            "lines": len(content.splitlines()),
                            "size": file_size,
                            "imports": extract_imports(content),
                            "classes": extract_classes(content),
                            "functions": extract_functions(content)
                        }
                except Exception as e:
                    print(f"  ⚠️ Error reading {file}: {e}")
            else:
                project_info["other_files"].append(file_path)
    
    # 결과 저장
    with open('project_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(project_info, f, indent=2, default=str)
    
    # 요약 출력
    print("\n" + "="*60)
    print("📊 프로젝트 분석 요약")
    print("="*60)
    print(f"총 Python 파일: {len(project_info['python_files'])}개")
    print(f"기타 파일: {len(project_info['other_files'])}개")
    print(f"\n주요 Python 파일:")
    for py_file in project_info['python_files']:
        info = project_info['file_contents'].get(py_file, {})
        print(f"  - {py_file}: {info.get('lines', 0)} lines")
    
    return project_info

def extract_imports(content):
    """import 문 추출"""
    imports = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
    return imports

def extract_classes(content):
    """클래스 이름 추출"""
    classes = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('class '):
            class_name = line.split('(')[0].replace('class ', '').strip(':')
            classes.append(class_name)
    return classes

def extract_functions(content):
    """함수 이름 추출"""
    functions = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('def ') or line.startswith('async def '):
            func_name = line.split('(')[0].replace('def ', '').replace('async ', '').strip()
            functions.append(func_name)
    return functions

if __name__ == "__main__":
    print("🔍 AIRISS 프로젝트 구조 분석 시작...\n")
    scan_project()
    print("\n✅ 분석 완료! 'project_analysis.json' 파일을 확인하세요.")