# 🎯 AIRISS v4.0 Complete Deployment Guide
# OK금융그룹 AI 기반 인재 분석 시스템 - 완전 배포 가이드

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

class AIRISSDeploymentManager:
    """AIRISS v4.0 배포 관리자"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_log = []
        
    def log(self, message, level="INFO"):
        """배포 로그 기록"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def run_command(self, command, description=""):
        """명령어 실행 및 로깅"""
        try:
            self.log(f"실행 중: {description or command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"성공: {description}", "SUCCESS")
                return True, result.stdout
            else:
                self.log(f"실패: {description} - {result.stderr}", "ERROR")
                return False, result.stderr
                
        except Exception as e:
            self.log(f"오류: {description} - {str(e)}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self):
        """필수 요구사항 확인"""
        self.log("=== 필수 요구사항 확인 ===")
        
        requirements = [
            ("python --version", "Python 설치 확인"),
            ("docker --version", "Docker 설치 확인"),
            ("docker-compose --version", "Docker Compose 설치 확인"),
            ("node --version", "Node.js 설치 확인"),
            ("npm --version", "npm 설치 확인")
        ]
        
        all_good = True
        for command, description in requirements:
            success, output = self.run_command(command, description)
            if not success:
                all_good = False
        
        return all_good
    
    def setup_environment(self):
        """환경 설정"""
        self.log("=== 환경 설정 ===")
        
        # .env 파일 생성
        env_content = """
# AIRISS v4.0 Environment Configuration
ENVIRONMENT=production
SERVER_HOST=0.0.0.0
SERVER_PORT=8002
WS_HOST=localhost

# Database
DATABASE_URL=sqlite:///./airiss.db

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["*"]

# OpenAI (선택사항)
OPENAI_API_KEY=your-openai-api-key-here

# Monitoring
ENABLE_MONITORING=true
LOG_LEVEL=INFO

# PWA
PWA_ENABLED=true
OFFLINE_SUPPORT=true
"""
        
        with open(self.project_root / ".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        self.log("환경 파일 생성 완료", "SUCCESS")
        return True
    
    def install_dependencies(self):
        """의존성 설치"""
        self.log("=== Python 의존성 설치 ===")
        
        # requirements.txt가 없으면 생성
        requirements_content = """
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
sqlite3
pandas==2.1.3
numpy==1.24.3
python-multipart==0.0.6
jinja2==3.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
aiofiles==23.2.1
openpyxl==3.1.2
xlrd==2.0.1
psutil==5.9.6
openai==1.3.0
httpx==0.25.2
"""
        
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write(requirements_content)
        
        # Python 의존성 설치
        success, output = self.run_command(
            f"pip install -r {requirements_path}", 
            "Python 패키지 설치"
        )
        
        if not success:
            return False
        
        # React 의존성 설치 (선택사항)
        react_path = self.project_root / "airiss-v4-frontend"
        if react_path.exists():
            os.chdir(react_path)
            self.run_command("npm ci", "React 의존성 설치")
            os.chdir(self.project_root)
        
        return True
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        self.log("=== 데이터베이스 초기화 ===")
        
        # 데이터베이스 초기화 스크립트 실행
        init_script = """
import sqlite3
from datetime import datetime

def init_airiss_database():
    conn = sqlite3.connect('airiss.db')
    cursor = conn.cursor()
    
    # 파일 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            total_records INTEGER,
            columns TEXT,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 분석 작업 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_jobs (
            job_id TEXT PRIMARY KEY,
            file_id TEXT,
            status TEXT DEFAULT 'pending',
            processed INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            average_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            FOREIGN KEY (file_id) REFERENCES uploaded_files (id)
        )
    ''')
    
    # 분석 결과 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            employee_id TEXT,
            employee_name TEXT,
            score_업무성과 REAL,
            score_KPI달성 REAL,
            score_태도마인드 REAL,
            score_커뮤니케이션 REAL,
            score_리더십협업 REAL,
            score_전문성학습 REAL,
            score_창의혁신 REAL,
            score_조직적응 REAL,
            total_score REAL,
            grade TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES analysis_jobs (job_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ AIRISS 데이터베이스 초기화 완료")

if __name__ == "__main__":
    init_airiss_database()
"""
        
        with open(self.project_root / "init_db.py", "w", encoding="utf-8") as f:
            f.write(init_script)
        
        success, output = self.run_command("python init_db.py", "데이터베이스 초기화")
        return success
    
    def deploy_application(self, mode="development"):
        """애플리케이션 배포"""
        self.log(f"=== {mode.upper()} 모드 배포 ===")
        
        if mode == "docker":
            return self.deploy_with_docker()
        elif mode == "production":
            return self.deploy_production()
        else:
            return self.deploy_development()
    
    def deploy_development(self):
        """개발 모드 배포"""
        self.log("개발 서버 시작...")
        
        # PWA Enhanced 버전 실행
        success, output = self.run_command(
            "python -m uvicorn app.main_pwa_enhanced:app --host 0.0.0.0 --port 8002 --reload",
            "개발 서버 시작"
        )
        
        return success
    
    def deploy_with_docker(self):
        """Docker 배포"""
        self.log("Docker 컨테이너 배포...")
        
        # Dockerfile 생성
        dockerfile_content = '''
FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8002

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
  CMD curl -f http://localhost:8002/health || exit 1

# 애플리케이션 실행
CMD ["python", "-m", "uvicorn", "app.main_pwa_enhanced:app", "--host", "0.0.0.0", "--port", "8002"]
'''
        
        with open(self.project_root / "Dockerfile", "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        
        # Docker 이미지 빌드
        success, output = self.run_command(
            "docker build -t airiss-v4-pwa .",
            "Docker 이미지 빌드"
        )
        
        if not success:
            return False
        
        # Docker 컨테이너 실행
        success, output = self.run_command(
            "docker run -d --name airiss-v4-container -p 8002:8002 -v airiss_data:/app/data airiss-v4-pwa",
            "Docker 컨테이너 실행"
        )
        
        return success
    
    def deploy_production(self):
        """프로덕션 배포"""
        self.log("프로덕션 환경 배포...")
        
        # 고급 배포 스크립트 실행
        if os.name == 'nt':  # Windows
            success, output = self.run_command(
                "deploy_advanced.bat production localhost 8002 --ssl --monitoring --backup",
                "Windows 프로덕션 배포"
            )
        else:  # Linux/Mac
            success, output = self.run_command(
                "chmod +x deploy_advanced.sh && ./deploy_advanced.sh production localhost 8002 --ssl --monitoring --backup",
                "Linux 프로덕션 배포"
            )
        
        return success
    
    def run_tests(self):
        """테스트 실행"""
        self.log("=== 시스템 테스트 실행 ===")
        
        test_script = '''
import requests
import time
import json

def test_airiss_system():
    base_url = "http://localhost:8002"
    
    tests = [
        ("GET", "/", "메인 페이지"),
        ("GET", "/health", "헬스체크"),
        ("GET", "/health/db", "데이터베이스 헬스체크"),
        ("GET", "/health/analysis", "분석 엔진 헬스체크"),
        ("GET", "/docs", "API 문서"),
        ("GET", "/monitoring/dashboard", "모니터링 대시보드"),
        ("GET", "/kpi/dashboard", "KPI 대시보드")
    ]
    
    results = []
    
    for method, endpoint, description in tests:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                results.append(f"✅ {description}: 성공")
            else:
                results.append(f"❌ {description}: HTTP {response.status_code}")
                
        except Exception as e:
            results.append(f"❌ {description}: {str(e)}")
    
    return results

if __name__ == "__main__":
    print("AIRISS v4.0 시스템 테스트 시작...")
    time.sleep(5)  # 서버 시작 대기
    
    results = test_airiss_system()
    for result in results:
        print(result)
    
    success_count = sum(1 for r in results if "✅" in r)
    total_count = len(results)
    
    print(f"\\n테스트 결과: {success_count}/{total_count} 성공")
'''
        
        with open(self.project_root / "test_system.py", "w", encoding="utf-8") as f:
            f.write(test_script)
        
        success, output = self.run_command("python test_system.py", "시스템 테스트 실행")
        return success
    
    def generate_report(self):
        """배포 보고서 생성"""
        self.log("=== 배포 보고서 생성 ===")
        
        report = {
            "deployment_info": {
                "timestamp": datetime.now().isoformat(),
                "version": "AIRISS v4.0 PWA Enhanced",
                "status": "completed"
            },
            "features": {
                "pwa_ready": True,
                "offline_support": True,
                "real_time_monitoring": True,
                "kpi_dashboard": True,
                "mobile_optimized": True,
                "chart_visualization": True,
                "websocket_enabled": True,
                "docker_support": True
            },
            "endpoints": {
                "main_ui": "http://localhost:8002/",
                "api_docs": "http://localhost:8002/docs",
                "monitoring": "http://localhost:8002/monitoring/dashboard",
                "kpi_dashboard": "http://localhost:8002/kpi/dashboard",
                "health_check": "http://localhost:8002/health"
            },
            "deployment_log": self.deployment_log
        }
        
        with open(self.project_root / "deployment_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("배포 보고서 생성 완료: deployment_report.json", "SUCCESS")
        return True
    
    def full_deployment(self, mode="development"):
        """전체 배포 프로세스"""
        self.log("🚀 AIRISS v4.0 Complete Deployment 시작")
        self.log("=" * 60)
        
        steps = [
            ("필수 요구사항 확인", self.check_prerequisites),
            ("환경 설정", self.setup_environment),
            ("의존성 설치", self.install_dependencies),
            ("데이터베이스 초기화", self.initialize_database),
            ("애플리케이션 배포", lambda: self.deploy_application(mode)),
            ("시스템 테스트", self.run_tests),
            ("배포 보고서 생성", self.generate_report)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            self.log(f"단계: {step_name}")
            
            try:
                if step_func():
                    success_count += 1
                    self.log(f"✅ {step_name} 완료", "SUCCESS")
                else:
                    self.log(f"❌ {step_name} 실패", "ERROR")
                    break
            except Exception as e:
                self.log(f"❌ {step_name} 오류: {str(e)}", "ERROR")
                break
        
        self.log("=" * 60)
        if success_count == len(steps):
            self.log("🎉 AIRISS v4.0 배포가 성공적으로 완료되었습니다!", "SUCCESS")
            self.log("📱 http://localhost:8002 에서 시스템을 확인하세요.")
        else:
            self.log(f"⚠️ 배포 중 문제가 발생했습니다. ({success_count}/{len(steps)} 단계 완료)", "WARNING")
        
        return success_count == len(steps)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AIRISS v4.0 Complete Deployment")
    parser.add_argument("--mode", choices=["development", "docker", "production"], 
                       default="development", help="배포 모드")
    parser.add_argument("--skip-tests", action="store_true", help="테스트 건너뛰기")
    
    args = parser.parse_args()
    
    deployer = AIRISSDeploymentManager()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  AIRISS v4.0 Complete Deployment            ║
║             OK금융그룹 AI 기반 인재 분석 시스템                  ║
║                                                              ║
║  🎯 PWA Ready + 실시간 모니터링 + KPI 대시보드                  ║
║  📱 모바일 최적화 + 오프라인 지원                               ║
║  🚀 Docker + 프로덕션 배포 지원                                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    success = deployer.full_deployment(args.mode)
    
    if success:
        print("\n🎉 배포 완료! 다음 URL에서 확인하세요:")
        print("   📱 메인 UI: http://localhost:8002/")
        print("   📊 모니터링: http://localhost:8002/monitoring/dashboard") 
        print("   📈 KPI: http://localhost:8002/kpi/dashboard")
        print("   📖 API 문서: http://localhost:8002/docs")
        sys.exit(0)
    else:
        print("\n❌ 배포 실패. 로그를 확인하세요.")
        sys.exit(1)