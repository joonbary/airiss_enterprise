#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIRISS v4.0 시스템 진단 도구
현재 시스템의 작동 상태를 체계적으로 점검합니다.
"""

import os
import sys
import json
import importlib
import subprocess
from datetime import datetime
from pathlib import Path

class AIRISSSystemDiagnostic:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "environment": {},
            "packages": {},
            "modules": {},
            "database": {},
            "services": {},
            "api_test": {},
            "recommendations": []
        }
        self.project_root = Path(__file__).parent
        
    def print_header(self, title):
        """섹션 헤더 출력"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
    def check_python_version(self):
        """Python 버전 확인"""
        self.print_header("Python 환경 확인")
        version = sys.version
        self.results["system_info"]["python_version"] = version
        print(f"✅ Python 버전: {sys.version.split()[0]}")
        
        # 권장 버전 확인
        major, minor = sys.version_info[:2]
        if major == 3 and minor >= 8:
            print("✅ Python 버전이 적절합니다 (3.8 이상)")
        else:
            print("⚠️ Python 3.8 이상을 권장합니다")
            self.results["recommendations"].append("Python 3.8 이상으로 업그레이드 권장")
            
    def check_required_packages(self):
        """필수 패키지 설치 확인"""
        self.print_header("필수 패키지 확인")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "pandas",
            "numpy",
            "scikit-learn",
            "sqlalchemy",
            "aiosqlite",
            "websockets",
            "jinja2"
        ]
        
        for package in required_packages:
            try:
                module = importlib.import_module(package.replace("-", "_"))
                version = getattr(module, "__version__", "unknown")
                self.results["packages"][package] = {"installed": True, "version": version}
                print(f"✅ {package}: {version}")
            except ImportError:
                self.results["packages"][package] = {"installed": False}
                print(f"❌ {package}: 설치되지 않음")
                self.results["recommendations"].append(f"pip install {package} 실행 필요")
                
    def check_project_structure(self):
        """프로젝트 구조 확인"""
        self.print_header("프로젝트 구조 확인")
        
        essential_dirs = ["app", "app/api", "app/services", "app/templates", "app/db"]
        essential_files = ["app/main.py", ".env", "requirements.txt"]
        
        for dir_path in essential_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"✅ {dir_path}/ 존재")
                self.results["system_info"][f"dir_{dir_path}"] = True
            else:
                print(f"❌ {dir_path}/ 없음")
                self.results["system_info"][f"dir_{dir_path}"] = False
                self.results["recommendations"].append(f"{dir_path} 디렉토리 생성 필요")
                
        for file_path in essential_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path} 존재")
                self.results["system_info"][f"file_{file_path}"] = True
            else:
                print(f"❌ {file_path} 없음")
                self.results["system_info"][f"file_{file_path}"] = False
                if file_path == ".env":
                    self.results["recommendations"].append(".env.example을 복사하여 .env 파일 생성 필요")
                    
    def check_core_modules(self):
        """핵심 모듈 import 테스트"""
        self.print_header("핵심 모듈 확인")
        
        # Python 경로에 프로젝트 루트 추가
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            
        core_modules = [
            ("app.main", "FastAPI 메인 앱"),
            ("app.db.sqlite_service", "SQLite 서비스"),
            ("app.services.text_analyzer", "텍스트 분석기"),
            ("app.services.quantitative_analyzer", "정량 분석기"),
            ("app.services.hybrid_analyzer", "하이브리드 분석기"),
            ("app.core.websocket_manager", "WebSocket 매니저")
        ]
        
        for module_name, description in core_modules:
            try:
                module = importlib.import_module(module_name)
                self.results["modules"][module_name] = True
                print(f"✅ {description} ({module_name})")
            except Exception as e:
                self.results["modules"][module_name] = False
                print(f"❌ {description} ({module_name}): {str(e)}")
                self.results["recommendations"].append(f"{module_name} 모듈 오류 수정 필요")
                
    def check_database(self):
        """데이터베이스 연결 테스트"""
        self.print_header("데이터베이스 확인")
        
        db_path = self.project_root / "airiss.db"
        if db_path.exists():
            print(f"✅ 데이터베이스 파일 존재: {db_path}")
            self.results["database"]["file_exists"] = True
            
            # 데이터베이스 크기 확인
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"📊 데이터베이스 크기: {size_mb:.2f} MB")
            self.results["database"]["size_mb"] = size_mb
        else:
            print("❌ 데이터베이스 파일이 없습니다")
            self.results["database"]["file_exists"] = False
            self.results["recommendations"].append("데이터베이스 초기화 필요 (init_database.py 실행)")
            
    def check_env_variables(self):
        """환경 변수 확인"""
        self.print_header("환경 변수 확인")
        
        env_path = self.project_root / ".env"
        if env_path.exists():
            print("✅ .env 파일 존재")
            
            # 필수 환경 변수 확인
            required_vars = ["SERVER_HOST", "SERVER_PORT", "WS_HOST"]
            
            # .env 파일 읽기
            env_vars = {}
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
                        
            for var in required_vars:
                if var in env_vars or var in os.environ:
                    value = env_vars.get(var, os.environ.get(var, ""))
                    print(f"✅ {var}: {value}")
                    self.results["environment"][var] = value
                else:
                    print(f"⚠️ {var}: 설정되지 않음")
                    self.results["environment"][var] = None
        else:
            print("❌ .env 파일이 없습니다")
            self.results["recommendations"].append(".env 파일 생성 필요")
            
    def test_basic_import(self):
        """기본 import 테스트"""
        self.print_header("기본 Import 테스트")
        
        test_code = """
import sys
sys.path.insert(0, r'{}')

try:
    from app.services.text_analyzer import AIRISSTextAnalyzer
    analyzer = AIRISSTextAnalyzer()
    print("✅ 텍스트 분석기 생성 성공")
    
    # 간단한 분석 테스트
    result = analyzer.analyze_text("좋은 성과를 보였습니다", "업무성과")
    print(f"✅ 분석 테스트 성공: 점수 = {result['score']}")
except Exception as e:
    print(f"❌ 텍스트 분석기 테스트 실패: {e}")
""".format(self.project_root)
        
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"오류: {result.stderr}")
            
    def generate_report(self):
        """진단 보고서 생성"""
        self.print_header("진단 결과 요약")
        
        # 전체 상태 판단
        all_good = True
        
        # 패키지 상태
        installed_packages = sum(1 for p in self.results["packages"].values() if p.get("installed", False))
        total_packages = len(self.results["packages"])
        print(f"\n📦 패키지: {installed_packages}/{total_packages} 설치됨")
        if installed_packages < total_packages:
            all_good = False
            
        # 모듈 상태
        working_modules = sum(1 for m in self.results["modules"].values() if m)
        total_modules = len(self.results["modules"])
        print(f"🔧 모듈: {working_modules}/{total_modules} 정상")
        if working_modules < total_modules:
            all_good = False
            
        # 데이터베이스 상태
        if self.results["database"].get("file_exists", False):
            print("💾 데이터베이스: 정상")
        else:
            print("💾 데이터베이스: 없음")
            all_good = False
            
        # 전체 상태
        if all_good:
            print("\n✅ 시스템 상태: 정상")
        else:
            print("\n⚠️ 시스템 상태: 일부 문제 발견")
            
        # 권장사항
        if self.results["recommendations"]:
            print("\n📋 권장 조치사항:")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
                
        # JSON 보고서 저장
        report_path = self.project_root / "system_diagnostic_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📄 상세 보고서 저장됨: {report_path}")
        
    def run_full_diagnostic(self):
        """전체 진단 실행"""
        print("🚀 AIRISS v4.0 시스템 진단 시작")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_python_version()
        self.check_required_packages()
        self.check_project_structure()
        self.check_core_modules()
        self.check_database()
        self.check_env_variables()
        self.test_basic_import()
        self.generate_report()
        
        print("\n✅ 진단 완료!")

if __name__ == "__main__":
    diagnostic = AIRISSSystemDiagnostic()
    diagnostic.run_full_diagnostic()
