"""
AIRISS v4.1 포트 충돌 해결 스크립트
자동으로 사용 가능한 포트를 찾아 서버를 실행합니다.
"""

import sys
import os
import socket
import subprocess
import time

def find_process_by_port(port):
    """특정 포트를 사용 중인 프로세스 찾기"""
    try:
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    return pid
    except:
        pass
    return None

def kill_process(pid):
    """프로세스 종료"""
    try:
        subprocess.run(['taskkill', '/PID', pid, '/F'], shell=True)
        print(f"✅ PID {pid} 프로세스를 종료했습니다.")
        time.sleep(2)  # 프로세스 종료 대기
        return True
    except:
        print(f"❌ PID {pid} 프로세스 종료 실패")
        return False

def is_port_available(port):
    """포트 사용 가능 여부 확인"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def find_available_port(start_port=8002, max_port=8010):
    """사용 가능한 포트 찾기"""
    for port in range(start_port, max_port):
        if is_port_available(port):
            return port
    return None

def main():
    print("="*80)
    print("🔧 AIRISS v4.1 포트 충돌 해결 도구")
    print("="*80)
    
    desired_port = 8002
    
    # 1. 포트 8002 상태 확인
    print(f"\n1️⃣ 포트 {desired_port} 상태 확인 중...")
    
    if is_port_available(desired_port):
        print(f"✅ 포트 {desired_port}를 사용할 수 있습니다!")
        port_to_use = desired_port
    else:
        print(f"⚠️ 포트 {desired_port}가 이미 사용 중입니다.")
        
        # 사용 중인 프로세스 찾기
        pid = find_process_by_port(desired_port)
        if pid:
            print(f"📌 PID {pid} 프로세스가 포트를 사용 중입니다.")
            
            # 프로세스 정보 표시
            try:
                result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {pid}'], 
                    capture_output=True, 
                    text=True, 
                    shell=True
                )
                print("\n프로세스 정보:")
                print(result.stdout)
            except:
                pass
            
            # 사용자 선택
            print("\n어떻게 하시겠습니까?")
            print("1. 기존 프로세스 종료하고 8002 포트 사용")
            print("2. 다른 포트 사용")
            print("3. 취소")
            
            choice = input("\n선택 (1/2/3): ")
            
            if choice == '1':
                if kill_process(pid):
                    if is_port_available(desired_port):
                        print(f"✅ 포트 {desired_port}가 사용 가능해졌습니다!")
                        port_to_use = desired_port
                    else:
                        print("❌ 포트가 여전히 사용 중입니다. 다른 포트를 찾습니다...")
                        port_to_use = find_available_port(8003)
                else:
                    port_to_use = find_available_port(8003)
            elif choice == '2':
                port_to_use = find_available_port(8003)
            else:
                print("👋 취소되었습니다.")
                return
        else:
            # 프로세스를 찾을 수 없는 경우 다른 포트 사용
            port_to_use = find_available_port(8003)
    
    if not port_to_use:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        return
    
    # 2. 서버 실행
    print(f"\n2️⃣ 포트 {port_to_use}에서 AIRISS v4.1 서버를 시작합니다...")
    print("="*80)
    print(f"\n✨ 접속 주소:")
    print(f"   - 메인 페이지: http://localhost:{port_to_use}/")
    print(f"   - API 문서: http://localhost:{port_to_use}/docs")
    print(f"   - 대시보드: http://localhost:{port_to_use}/dashboard")
    print(f"\n💡 종료하려면 Ctrl+C를 누르세요.\n")
    print("="*80 + "\n")
    
    # uvicorn 실행
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', str(port_to_use),
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n👋 서버를 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
