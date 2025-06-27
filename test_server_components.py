"""
AIRISS v4.0 서버 컴포넌트 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=== AIRISS v4.0 서버 컴포넌트 테스트 시작 ===\n")

# 1. 기본 모듈 import 테스트
print("1. 기본 모듈 import 테스트...")
try:
    from app.core.websocket_manager import ConnectionManager
    print("✅ WebSocket Manager: OK")
except Exception as e:
    print(f"❌ WebSocket Manager: {e}")

try:
    from app.db.sqlite_service import SQLiteService
    print("✅ SQLite Service: OK")
except Exception as e:
    print(f"❌ SQLite Service: {e}")

# 2. 분석 모듈 테스트
print("\n2. 분석 모듈 테스트...")
try:
    from app.services.text_analyzer import AIRISSTextAnalyzer
    print("✅ Text Analyzer: OK")
except Exception as e:
    print(f"❌ Text Analyzer: {e}")

try:
    from app.services.quantitative_analyzer import QuantitativeAnalyzer
    print("✅ Quantitative Analyzer: OK")
except Exception as e:
    print(f"❌ Quantitative Analyzer: {e}")

try:
    from app.services import HybridAnalyzer
    print("✅ Hybrid Analyzer: OK")
except Exception as e:
    print(f"❌ Hybrid Analyzer: {e}")

try:
    from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
    print("✅ AIRISSHybridAnalyzer: OK")
except Exception as e:
    print(f"❌ AIRISSHybridAnalyzer: {e}")

# 3. 고급 분석 모듈 테스트
print("\n3. 고급 분석 모듈 테스트...")
try:
    from app.services.bias_detection import BiasDetector
    detector = BiasDetector()
    print("✅ Bias Detector: OK (초기화 성공)")
except Exception as e:
    print(f"❌ Bias Detector: {e}")

try:
    from app.services.predictive_analytics import PerformancePredictor
    predictor = PerformancePredictor()
    print("✅ Performance Predictor: OK (초기화 성공)")
except Exception as e:
    print(f"❌ Performance Predictor: {e}")

# 4. API 라우터 테스트
print("\n4. API 라우터 테스트...")
try:
    from app.api.upload import router as upload_router
    print("✅ Upload Router: OK")
except Exception as e:
    print(f"❌ Upload Router: {e}")

try:
    from app.api.analysis import router as analysis_router
    print("✅ Analysis Router: OK")
except Exception as e:
    print(f"❌ Analysis Router: {e}")

# 5. 메인 앱 테스트
print("\n5. 메인 앱 테스트...")
try:
    from app.main_enhanced import app
    print("✅ Main Enhanced App: OK")
    
    # FastAPI 앱 정보 확인
    print(f"   - 앱 이름: {app.title}")
    print(f"   - 앱 버전: {app.version}")
    print(f"   - 라우트 수: {len(app.routes)}")
except Exception as e:
    print(f"❌ Main Enhanced App: {e}")

# 6. 필수 패키지 확인
print("\n6. 필수 패키지 확인...")
packages = [
    'fastapi', 'uvicorn', 'pandas', 'numpy', 
    'scipy', 'scikit-learn', 'joblib', 'websockets'
]

for package in packages:
    try:
        __import__(package)
        print(f"✅ {package}: OK")
    except ImportError:
        print(f"❌ {package}: 설치 필요")

# 7. 데이터베이스 파일 확인
print("\n7. 데이터베이스 파일 확인...")
db_file = "airiss.db"
if os.path.exists(db_file):
    print(f"✅ 데이터베이스 파일 존재: {db_file} ({os.path.getsize(db_file)} bytes)")
else:
    print(f"⚠️ 데이터베이스 파일 없음: {db_file}")

# 8. 업로드 폴더 확인
print("\n8. 업로드 폴더 확인...")
upload_dir = "uploads"
if os.path.exists(upload_dir):
    files = os.listdir(upload_dir)
    print(f"✅ 업로드 폴더 존재: {len(files)}개 파일")
else:
    print(f"⚠️ 업로드 폴더 없음: {upload_dir}")
    os.makedirs(upload_dir, exist_ok=True)
    print(f"✅ 업로드 폴더 생성됨: {upload_dir}")

print("\n=== 테스트 완료 ===")
print("\n서버를 시작하려면 다음 명령어를 실행하세요:")
print("1. start_enhanced_v4.bat (권장)")
print("2. python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8002 --reload")
