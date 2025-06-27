# simple_structure.py
import os
from pathlib import Path

print("🔍 AIRISS 프로젝트 구조\n")
print("=" * 60)

# Python 파일만 찾기
py_files = []
for root, dirs, files in os.walk("."):
    # 제외할 폴더
    if any(skip in root for skip in ['__pycache__', 'venv', '.git', 'env']):
        continue
    
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            size = os.path.getsize(path) // 1024  # KB
            py_files.append((path, size))

# 크기 순으로 정렬
py_files.sort(key=lambda x: x[1], reverse=True)

print("📁 주요 Python 파일들 (크기 순):")
for path, size in py_files[:20]:  # 상위 20개만
    print(f"  {path} ({size}KB)")

print("\n📊 요약:")
print(f"총 Python 파일 수: {len(py_files)}개")