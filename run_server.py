"""
AIRISS v4.1 실행 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# main 모듈 임포트 및 실행
if __name__ == "__main__":
    from app.main import app
    import uvicorn
    
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8002"))
    
    print("🚀 AIRISS v4.1 Enhanced 서버 시작...")
    print(f"📍 접속 주소: http://localhost:{SERVER_PORT}/")
    
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
        reload=False,
        access_log=True
    )
