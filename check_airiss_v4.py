# check_airiss_v4.py
"""AIRISS v4.0 Enhanced 시스템 진단 스크립트"""

import sys
import os
import importlib
import json
from datetime import datetime

print("=" * 60)
print("🔍 AIRISS v4.0 Enhanced 시스템 진단")
print("=" * 60)
print()

# 진단 결과 저장
diagnostic_results = {
    "timestamp": datetime.now().isoformat(),
    "python_version": sys.version,
    "checks": []
}

def check_module(module_name, required=True):
    """모듈 존재 확인"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} 모듈 확인됨")
        diagnostic_results["checks"].append({
            "module": module_name,
            "status": "success",
            "required": required
        })
        return True
    except ImportError as e:
        if required:
            print(f"❌ {module_name} 모듈 없음: {e}")
        else:
            print(f"⚠️ {module_name} 모듈 없음 (선택적)")
        diagnostic_results["checks"].append({
            "module": module_name,
            "status": "failed",
            "required": required,
            "error": str(e)
        })
        return False

def check_file(file_path, required=True):
    """파일 존재 확인"""
    exists = os.path.exists(file_path)
    if exists:
        print(f"✅ {file_path} 파일 확인됨")
        diagnostic_results["checks"].append({
            "file": file_path,
            "status": "success",
            "required": required
        })
    else:
        if required:
            print(f"❌ {file_path} 파일 없음")
        else:
            print(f"⚠️ {file_path} 파일 없음 (선택적)")
        diagnostic_results["checks"].append({
            "file": file_path,
            "status": "failed",
            "required": required
        })
    return exists

print("1. 필수 패키지 확인")
print("-" * 40)
required_modules = [
    "fastapi",
    "uvicorn",
    "pandas",
    "numpy",
    "sqlalchemy",
    "openpyxl",
    "websockets",
    "pydantic"
]

for module in required_modules:
    check_module(module)

print("\n2. 프로젝트 모듈 확인")
print("-" * 40)
project_modules = [
    "app.main_enhanced",
    "app.core.websocket_manager",
    "app.api.analysis",
    "app.db.sqlite_service",
    "app.services.text_analyzer",
    "app.services.quantitative_analyzer",
    "app.services.hybrid_analyzer"
]

for module in project_modules:
    check_module(module)

print("\n3. 선택적 모듈 확인")
print("-" * 40)
optional_modules = [
    ("app.services.bias_detection", "편향 탐지"),
    ("app.services.predictive_analytics", "예측 분석"),
    ("openai", "OpenAI GPT 지원"),
    ("transformers", "고급 NLP 분석")
]

for module, desc in optional_modules:
    if check_module(module, required=False):
        print(f"   ➡️ {desc} 기능 사용 가능")

print("\n4. 핵심 파일 확인")
print("-" * 40)
core_files = [
    "app/__init__.py",
    "app/main_enhanced.py",
    "app/api/__init__.py",
    "app/api/analysis.py",
    "app/services/__init__.py",
    "requirements.txt"
]

for file in core_files:
    check_file(file)

print("\n5. 환경 설정 확인")
print("-" * 40)
env_vars = {
    "SERVER_HOST": os.getenv("SERVER_HOST", "0.0.0.0"),
    "SERVER_PORT": os.getenv("SERVER_PORT", "8002"),
    "WS_HOST": os.getenv("WS_HOST", "localhost")
}

for var, value in env_vars.items():
    print(f"📌 {var}: {value}")

print("\n6. SQLite DB 확인")
print("-" * 40)
if check_file("airiss.db", required=False):
    try:
        import sqlite3
        conn = sqlite3.connect("airiss.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM uploaded_files")
        file_count = cursor.fetchone()[0]
        print(f"   ➡️ 업로드된 파일 수: {file_count}")
        conn.close()
    except Exception as e:
        print(f"   ⚠️ DB 접근 오류: {e}")

# 진단 결과 저장
with open("diagnostic_report.json", "w", encoding="utf-8") as f:
    json.dump(diagnostic_results, f, indent=2, ensure_ascii=False)

# 최종 결과
print("\n" + "=" * 60)
total_checks = len(diagnostic_results["checks"])
failed_checks = [c for c in diagnostic_results["checks"] if c["status"] == "failed" and c.get("required", True)]
optional_failed = [c for c in diagnostic_results["checks"] if c["status"] == "failed" and not c.get("required", True)]

if not failed_checks:
    print("✅ 시스템 진단 완료: 모든 필수 항목 정상")
    print(f"   - 총 검사 항목: {total_checks}")
    print(f"   - 선택적 미설치: {len(optional_failed)}")
    print("\n🚀 AIRISS v4.0 Enhanced를 실행할 준비가 되었습니다!")
    print("   실행 명령: python -m app.main_enhanced")
else:
    print(f"❌ 시스템 진단 실패: {len(failed_checks)}개 필수 항목 문제")
    print("\n문제 해결 방법:")
    print("1. pip install -r requirements.txt 실행")
    print("2. 프로젝트 파일 구조 확인")
    print("3. Python 경로 설정 확인")

print("\n자세한 진단 결과는 diagnostic_report.json 파일을 확인하세요.")
print("=" * 60)
