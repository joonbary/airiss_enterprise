import subprocess
import sys
import os

# 현재 디렉토리 설정
os.chdir(r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4")

# 테스트 실행
print("AIRISS v4.0 서버 컴포넌트 테스트 실행 중...\n")

try:
    # Python 실행
    result = subprocess.run(
        [sys.executable, "test_server_components.py"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    print("=== 출력 결과 ===")
    print(result.stdout)
    
    if result.stderr:
        print("\n=== 오류 출력 ===")
        print(result.stderr)
        
    print(f"\n실행 완료. 반환 코드: {result.returncode}")
    
except Exception as e:
    print(f"테스트 실행 중 오류 발생: {e}")
