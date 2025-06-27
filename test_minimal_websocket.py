# test_minimal_websocket.py
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("WebSocket 연결 시도 감지!")  # 디버깅용
    await websocket.accept()
    print("WebSocket 연결 수락됨!")
    await websocket.send_text("연결 성공!")
    await websocket.close()

@app.get("/")
async def root():
    return {"message": "WebSocket 테스트 서버 실행 중"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")