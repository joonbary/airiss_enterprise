"""
AIRISS v4.0 필수 패키지 확인 및 설치 스크립트
"""

import subprocess
import sys
import importlib.util

print("=" * 60)
print("AIRISS v4.0 필수 패키지 확인")
print("=" * 60)

# 필수 패키지 목록
required_packages = {
    # 기본 웹 프레임워크
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn[standard]',
    'websockets': 'websockets',
    'aiofiles': 'aiofiles',
    
    # 데이터 분석
    'pandas': 'pandas',
    'numpy': 'numpy',
    'scipy': 'scipy',
    'sklearn': 'scikit-learn',
    'joblib': 'joblib',
    
    # 데이터베이스
    'sqlalchemy': 'sqlalchemy',
    
    # Excel 처리
    'openpyxl': 'openpyxl',
    'xlrd': 'xlrd',
    
    # HTTP 클라이언트 (테스트용)
    'aiohttp': 'aiohttp',
    
    # 기타
    'pydantic': 'pydantic',
    'python-multipart': 'python-multipart',
}

# 선택적 패키지 (없어도 기본 기능은 작동)
optional_packages = {
    'openai': 'openai',  # AI 피드백 기능
    'redis': 'redis',    # Redis 캐싱
}

def check_package(package_name):
    """패키지 설치 여부 확인"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_install_name):
    """패키지 설치"""
    try:
        print(f"  설치 중: {package_install_name}...", end="", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_install_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(" ✅ 완료")
            return True
        else:
            print(f" ❌ 실패\n  오류: {result.stderr}")
            return False
    except Exception as e:
        print(f" ❌ 실패: {e}")
        return False

# 필수 패키지 확인
print("\n1. 필수 패키지 확인...")
missing_required = []

for import_name, install_name in required_packages.items():
    if check_package(import_name):
        print(f"✅ {import_name}: 설치됨")
    else:
        print(f"❌ {import_name}: 미설치")
        missing_required.append((import_name, install_name))

# 선택적 패키지 확인
print("\n2. 선택적 패키지 확인...")
missing_optional = []

for import_name, install_name in optional_packages.items():
    if check_package(import_name):
        print(f"✅ {import_name}: 설치됨")
    else:
        print(f"⚠️ {import_name}: 미설치 (선택사항)")
        missing_optional.append((import_name, install_name))

# 설치 필요 여부 확인
if missing_required:
    print(f"\n⚠️ {len(missing_required)}개의 필수 패키지가 설치되지 않았습니다.")
    response = input("\n필수 패키지를 자동으로 설치하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        print("\n필수 패키지 설치 시작...")
        success_count = 0
        
        for import_name, install_name in missing_required:
            if install_package(install_name):
                success_count += 1
        
        print(f"\n설치 완료: {success_count}/{len(missing_required)}")
        
        if success_count == len(missing_required):
            print("✅ 모든 필수 패키지가 설치되었습니다!")
        else:
            print("❌ 일부 패키지 설치에 실패했습니다. 수동으로 설치해주세요.")
    else:
        print("\n수동 설치 명령어:")
        for _, install_name in missing_required:
            print(f"  pip install {install_name}")
else:
    print("\n✅ 모든 필수 패키지가 이미 설치되어 있습니다!")

# 선택적 패키지 설치 제안
if missing_optional:
    print(f"\n선택적 패키지 {len(missing_optional)}개가 설치되지 않았습니다.")
    print("다음 기능을 사용하려면 설치가 필요합니다:")
    
    if any('openai' in pkg for pkg, _ in missing_optional):
        print("  - OpenAI GPT 기반 AI 피드백 기능")
    if any('redis' in pkg for pkg, _ in missing_optional):
        print("  - Redis 기반 고성능 캐싱")
    
    response = input("\n선택적 패키지를 설치하시겠습니까? (y/n): ")
    
    if response.lower() == 'y':
        print("\n선택적 패키지 설치 시작...")
        for import_name, install_name in missing_optional:
            install_package(install_name)

# Python 버전 확인
print(f"\n3. Python 버전 확인...")
python_version = sys.version_info
print(f"현재 Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major == 3 and python_version.minor >= 8:
    print("✅ Python 버전 적합 (3.8 이상)")
else:
    print("⚠️ Python 3.8 이상을 권장합니다.")

# 최종 안내
print("\n" + "=" * 60)
print("설정 완료!")
print("=" * 60)

if not missing_required:
    print("\n서버를 시작할 준비가 되었습니다!")
    print("\n실행 방법:")
    print("  1. start_enhanced_v4.bat (권장)")
    print("  2. python -m uvicorn app.main_enhanced:app --host 0.0.0.0 --port 8002 --reload")
    print("\n테스트 실행:")
    print("  python test_airiss_v4_integration.py")
else:
    print("\n⚠️ 필수 패키지를 먼저 설치해주세요.")

print("\n문서:")
print("  - 빠른 시작 가이드: QUICK_START_GUIDE.md")
print("  - 통합 가이드: INTEGRATION_COMPLETE_GUIDE.md")
print("  - 상용화 가이드: COMMERCIALIZATION_GUIDE.md")
