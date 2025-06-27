"""
AIRISS v4.1 디버깅 및 진단 스크립트
서버 실행 전 환경을 검사하고 문제를 진단합니다.
"""

import sys
import os
import socket
import subprocess
import importlib.util

def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    print(f"✅ Python 버전: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 이상이 필요합니다!")
        return False
    return True

def check_port(port=8002):
    """포트 사용 가능 여부 확인"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        print(f"❌ 포트 {port}가 이미 사용 중입니다!")
        print(f"💡 다음 명령으로 포트를 사용 중인 프로세스를 확인하세요:")
        print(f"   Windows: netstat -ano | findstr :{port}")
        return False
    else:
        print(f"✅ 포트 {port} 사용 가능")
        return True

def check_required_modules():
    """필수 모듈 확인"""
    required_modules = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'openpyxl',
        'websockets',
        'sqlalchemy',
        'aiofiles',
        'python-multipart'
    ]
    
    missing_modules = []
    
    for module_name in required_modules:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            missing_modules.append(module_name)
            print(f"❌ {module_name} 모듈이 설치되지 않았습니다")
        else:
            print(f"✅ {module_name} 모듈 확인됨")
    
    return missing_modules

def check_airiss_modules():
    """AIRISS 프로젝트 모듈 확인"""
    print("\n🔍 AIRISS 모듈 확인 중...")
    
    # 현재 디렉토리를 Python 경로에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        from app.main import app
        print("✅ app.main 모듈 로드 성공")
    except Exception as e:
        print(f"❌ app.main 모듈 로드 실패: {e}")
        return False
    
    try:
        from app.core.websocket_manager import ConnectionManager
        print("✅ ConnectionManager 모듈 로드 성공")
    except Exception as e:
        print(f"❌ ConnectionManager 모듈 로드 실패: {e}")
        return False
    
    try:
        from app.db.sqlite_service import SQLiteService
        print("✅ SQLiteService 모듈 로드 성공")
    except Exception as e:
        print(f"❌ SQLiteService 모듈 로드 실패: {e}")
        return False
    
    try:
        from app.api.upload import router as upload_router
        print("✅ Upload API 라우터 로드 성공")
    except Exception as e:
        print(f"❌ Upload API 라우터 로드 실패: {e}")
        
    try:
        from app.api.analysis import router as analysis_router
        print("✅ Analysis API 라우터 로드 성공")
    except Exception as e:
        print(f"❌ Analysis API 라우터 로드 실패: {e}")
    
    return True

def install_missing_packages(missing_modules):
    """누락된 패키지 설치"""
    if not missing_modules:
        return
    
    print(f"\n📦 누락된 패키지 설치 중...")
    cmd = [sys.executable, "-m", "pip", "install"] + missing_modules
    
    try:
        subprocess.check_call(cmd)
        print("✅ 패키지 설치 완료")
    except subprocess.CalledProcessError:
        print("❌ 패키지 설치 실패")

def main():
    """메인 진단 함수"""
    print("="*80)
    print("🔧 AIRISS v4.1 서버 진단 시작")
    print("="*80)
    
    # 1. Python 버전 확인
    print("\n1️⃣ Python 환경 확인")
    if not check_python_version():
        return
    
    # 2. 포트 확인
    print("\n2️⃣ 네트워크 포트 확인")
    if not check_port():
        return
    
    # 3. 필수 모듈 확인
    print("\n3️⃣ 필수 패키지 확인")
    missing = check_required_modules()
    
    if missing:
        print(f"\n⚠️ {len(missing)}개의 패키지가 누락되었습니다.")
        response = input("설치하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            install_missing_packages(missing)
    
    # 4. AIRISS 모듈 확인
    print("\n4️⃣ AIRISS 프로젝트 모듈 확인")
    if not check_airiss_modules():
        print("\n❌ AIRISS 모듈 로드 중 문제가 발생했습니다.")
        return
    
    # 5. 서버 실행 준비 완료
    print("\n" + "="*80)
    print("✅ 모든 검사를 통과했습니다!")
    print("🚀 서버를 실행할 준비가 되었습니다.")
    print("="*80)
    
    # 서버 실행 여부 확인
    response = input("\n서버를 실행하시겠습니까? (y/n): ")
    if response.lower() == 'y':
        print("\n🚀 서버를 시작합니다...")
        os.system("python run_server.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 진단을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 진단 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
