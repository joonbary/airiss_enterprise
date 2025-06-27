import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.main import app
    print("✅ app.main 모듈 임포트 성공")
    
    # 필수 모듈들 확인
    from app.core.websocket_manager import ConnectionManager
    print("✅ ConnectionManager 임포트 성공")
    
    from app.db.sqlite_service import SQLiteService
    print("✅ SQLiteService 임포트 성공")
    
    # API 라우터 확인
    try:
        from app.api.upload import router as upload_router
        print("✅ Upload router 임포트 성공")
    except Exception as e:
        print(f"❌ Upload router 임포트 실패: {e}")
    
    try:
        from app.api.analysis import router as analysis_router
        print("✅ Analysis router 임포트 성공")
    except Exception as e:
        print(f"❌ Analysis router 임포트 실패: {e}")
    
    print("\n🎉 모든 모듈 테스트 성공!")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
