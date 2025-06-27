import asyncio
import sys
sys.path.insert(0, ".")

from app.db.sqlite_service import SQLiteService
from app.api.analysis import hybrid_analyzer

async def test_analysis():
    """AIRISS v4.0 분석 엔진 테스트"""
    print("🧪 AIRISS v4.0 분석 엔진 테스트 시작...")
    
    # 1. SQLite 서비스 테스트
    print("\n1️⃣ SQLite 서비스 테스트")
    try:
        db_service = SQLiteService()
        await db_service.init_database()
        print("✅ SQLite 서비스 초기화 성공")
        
        files = await db_service.list_files()
        print(f"✅ 파일 수: {len(files)}개")
    except Exception as e:
        print(f"❌ SQLite 서비스 오류: {e}")
        return
    
    # 2. 분석 엔진 테스트
    print("\n2️⃣ 분석 엔진 테스트")
    try:
        test_text = "매우 우수한 성과를 보이며 KPI를 초과 달성했습니다. 팀워크도 뛰어나고 적극적입니다."
        
        # 텍스트 분석 테스트
        result = hybrid_analyzer.text_analyzer.analyze_text(test_text, "업무성과")
        print(f"✅ 텍스트 분석 성공: 점수 = {result['score']}")
        
        # 전체 8대 영역 분석
        print("\n📊 8대 영역 분석 결과:")
        from app.api.analysis import AIRISS_FRAMEWORK
        for dimension in AIRISS_FRAMEWORK.keys():
            result = hybrid_analyzer.text_analyzer.analyze_text(test_text, dimension)
            print(f"  - {dimension}: {result['score']}점")
            
    except Exception as e:
        print(f"❌ 분석 엔진 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. WebSocket 테스트
    print("\n3️⃣ WebSocket 매니저 테스트")
    try:
        from app.core.websocket_manager import ConnectionManager
        ws_manager = ConnectionManager()
        print("✅ WebSocket 매니저 초기화 성공")
    except Exception as e:
        print(f"❌ WebSocket 매니저 오류: {e}")
    
    print("\n✅ 모든 테스트 완료!")
    print("\n💡 다음 단계:")
    print("1. 서버를 재시작하세요: python run_server.py")
    print("2. 브라우저에서 http://localhost:8002 접속")
    print("3. 시스템 테스트 버튼 클릭")
    print("4. 샘플 데이터로 분석 테스트")

if __name__ == "__main__":
    asyncio.run(test_analysis())
