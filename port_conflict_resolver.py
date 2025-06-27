# port_conflict_resolver.py
# AIRISS v4.0 포트 충돌 해결 스크립트

import subprocess
import sys
import time

def find_processes_using_port(port=8002):
    """포트를 사용하는 프로세스 찾기"""
    try:
        # Windows의 netstat 명령어로 포트 사용 프로세스 찾기
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        using_processes = []
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    using_processes.append(pid)
        
        return using_processes
    except Exception as e:
        print(f"❌ 프로세스 검색 오류: {e}")
        return []

def kill_process(pid):
    """프로세스 종료"""
    try:
        subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
        print(f"✅ 프로세스 {pid} 종료 완료")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 프로세스 {pid} 종료 실패")
        return False

def main():
    print("🔍 AIRISS v4.0 포트 충돌 해결 도구")
    print("=" * 50)
    
    # 1. 포트 8002를 사용하는 프로세스 찾기
    print("1단계: 포트 8002를 사용하는 프로세스 검색 중...")
    processes = find_processes_using_port(8002)
    
    if not processes:
        print("✅ 포트 8002를 사용하는 프로세스가 없습니다.")
        print("🚀 이제 서버를 다시 실행해보세요: python app\\main.py")
        return
    
    print(f"🔍 포트 8002를 사용하는 프로세스: {processes}")
    
    # 2. 사용자 확인
    print("\n다음 프로세스들을 종료하시겠습니까?")
    for pid in processes:
        try:
            # 프로세스 이름 확인
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                  capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if pid in line:
                        print(f"  - PID {pid}: {line.split()[0] if line.split() else 'Unknown'}")
        except:
            print(f"  - PID {pid}: (프로세스 정보 확인 불가)")
    
    response = input("\n종료하시겠습니까? (y/N): ").strip().lower()
    
    if response != 'y':
        print("🔚 사용자에 의해 취소되었습니다.")
        print("\n💡 수동으로 프로세스를 종료하거나 다른 포트를 사용하세요.")
        print("   - Ctrl+C로 실행 중인 서버 종료")
        print("   - 작업 관리자에서 python.exe 프로세스 종료")
        print("   - 또는 다른 포트 사용: python app\\main.py --port 8003")
        return
    
    # 3. 프로세스 종료
    print("\n2단계: 프로세스 종료 중...")
    success_count = 0
    for pid in processes:
        if kill_process(pid):
            success_count += 1
        time.sleep(0.5)  # 잠시 대기
    
    print(f"\n📊 결과: {success_count}/{len(processes)} 프로세스 종료 완료")
    
    if success_count == len(processes):
        print("🎉 모든 프로세스가 성공적으로 종료되었습니다!")
        print("\n🚀 이제 AIRISS v4.0 서버를 실행하세요:")
        print("   python app\\main.py")
    else:
        print("⚠️ 일부 프로세스 종료에 실패했습니다.")
        print("   수동으로 작업 관리자를 통해 종료하거나 시스템을 재시작하세요.")

if __name__ == "__main__":
    main()