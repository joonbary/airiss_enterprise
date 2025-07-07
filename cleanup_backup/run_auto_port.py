"""
AIRISS v4.1 - 포트 변경 가능한 실행 스크립트
"""

import sys
import os
import uvicorn
import socket

def find_available_port(start_port=8002, max_attempts=10):
    """사용 가능한 포트 찾기"""
    for port in range(start_port, start_port + max_attempts):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result != 0:  # 포트가 사용 가능함
            return port
    return None

def main():
    """메인 실행 함수"""
    # 사용 가능한 포트 찾기
    port = find_available_port(8002)
    
    if port is None:
        print("❌ 사용 가능한 포트를 찾을 수 없습니다.")
        print("💡 실행 중인 AIRISS 서버를 종료하거나 다른 포트 범위를 시도하세요.")
        return
    
    print("\n" + "="*80)
    print(f"🚀 AIRISS v4.1 Enhanced Server Starting on Port {port}...")
    print("="*80)
    print(f"\n✨ 서버 시작 중... (포트 {port})")
    print(f"   - 메인 페이지: http://localhost:{port}/")
    print(f"   - API 문서: http://localhost:{port}/docs")
    print(f"   - 대시보드: http://localhost:{port}/dashboard")
    print("\n💡 종료하려면 Ctrl+C를 누르세요.\n")
    print("="*80 + "\n")
    
    # 환경 변수 설정
    os.environ['SERVER_PORT'] = str(port)
    
    try:
        # uvicorn으로 서버 실행
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 서버를 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 실패: {e}")

if __name__ == "__main__":
    main()
