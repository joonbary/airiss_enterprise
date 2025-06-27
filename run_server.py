"""
AIRISS v4.1 서버 실행 스크립트
간단하게 서버를 실행하기 위한 스크립트입니다.
"""

import sys
import os
import uvicorn
import logging

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
    try:
        # 서버 정보 출력
        print("\n" + "="*80)
        print("🚀 AIRISS v4.1 Enhanced Server Starting...")
        print("="*80)
        print("\n✨ 서버 시작 중...")
        print("   - 메인 페이지: http://localhost:8002/")
        print("   - API 문서: http://localhost:8002/docs")
        print("   - 대시보드: http://localhost:8002/dashboard")
        print("\n💡 종료하려면 Ctrl+C를 누르세요.\n")
        print("="*80 + "\n")
        
        # uvicorn으로 서버 실행
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8002,
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
        print("1. 필요한 패키지 설치: pip install -r requirements.txt")
        print("2. Python 버전 확인 (3.8 이상)")
        print("3. 포트 8002가 사용 중인지 확인")
        sys.exit(1)

if __name__ == "__main__":
    main()
