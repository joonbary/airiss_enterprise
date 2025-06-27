# test_websocket.py
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    # Job ID (실제 분석 작업의 ID로 변경)
    job_id = "your-actual-job-id"  # 또는 None
    
    uri = f"ws://localhost:8001/api/v1/ws?job_id={job_id}" if job_id else "ws://localhost:8001/api/v1/ws"
    
    async with websockets.connect(uri) as websocket:
        print(f"✅ WebSocket 연결 성공: {uri}")
        
        # 연결 확인 메시지 수신
        message = await websocket.recv()
        data = json.loads(message)
        print(f"📨 수신: {json.dumps(data, indent=2)}")
        
        # Ping 테스트
        await websocket.send(json.dumps({"type": "ping"}))
        print("📤 Ping 전송")
        
        # 메시지 수신 대기
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"\n📨 [{datetime.now().strftime('%H:%M:%S')}] 수신:")
                print(json.dumps(data, indent=2))
                
                # 진행률 업데이트 처리
                if data.get("type") == "progress_update":
                    print(f"📊 진행률: {data['progress']}% - 현재: {data.get('current_employee', 'N/A')}")
                
                elif data.get("type") == "analysis_complete":
                    print("🎉 분석 완료!")
                    print(f"요약: {data.get('results_summary', {})}")
                    break
                
                elif data.get("type") == "error":
                    print(f"❌ 오류: {data['error']}")
                    break
                    
        except KeyboardInterrupt:
            print("\n⏹️  테스트 중단")

if __name__ == "__main__":
    asyncio.run(test_websocket())