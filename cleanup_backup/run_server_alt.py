"""
AIRISS v4.1 서버 실행 스크립트 (포트 설정 가능)
"""

import sys
import os
import uvicorn
import logging
import argparse

# 프로젝트 루트 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """메인 실행 함수"""
    # 명령줄 인자 파서
    parser = argparse.ArgumentParser(description='AIRISS v4.1 서버 실행')
    parser.add_argument('--port', type=int, default=8002, help='서버 포트 (기본값: 8002)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='서버 호스트 (기본값: 0.0.0.0)')
    args = parser.parse_args()
    
    try:
        # 서버 정보 출력
        print("\n" + "="*80)
        print("🚀 AIRISS v4.1 Enhanced Server Starting...")
        print("="*80)
        print(f"\n✨ 서버 시작 중... (포트: {args.port})")
        print(f"   - 메인 페이지: http://localhost:{args.port}/")
        print(f"   - API 문서: http://localhost:{args.port}/docs")
        print(f"   - 대시보드: http://localhost:{args.port}/dashboard")
        print("\n💡 종료하려면 Ctrl+C를 누르세요.\n")
        print("="*80 + "\n")
        
        # 환경 변수로 포트 설정
        os.environ['SERVER_PORT'] = str(args.port)
        
        # uvicorn으로 서버 실행
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {e}")
        print(f"\n❌ 서버 실행 실패: {e}")
        print("\n디버깅 정보:")
        print("-" * 40)
        import traceback
        traceback.print_exc()
        print("-" * 40)
        print("\n💡 해결 방법:")
        print("1. 다른 포트 사용: python run_server_alt.py --port 8003")
        print("2. 필요한 패키지 설치: pip install -r requirements.txt")
        print("3. Python 버전 확인 (3.8 이상)")
        sys.exit(1)

if __name__ == "__main__":
    main()
