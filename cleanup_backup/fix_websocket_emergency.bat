@echo off
REM AIRISS WebSocket 문제 긴급 수정 스크립트 (Windows)

echo 🔧 AIRISS WebSocket 긴급 수정 시작...
echo ==================================

REM 1. Backend 서버 상태 확인
echo 1️⃣ Backend 서버 상태 확인...
python debug_backend_websocket.py

REM 2. Frontend 포트 설정 확인
echo.
echo 2️⃣ Frontend 포트 설정 확인...
if exist "airiss-v4-frontend\.env" (
    echo 📝 현재 .env 설정:
    findstr "PORT" airiss-v4-frontend\.env
    echo ✅ 포트가 3001로 설정되었습니다.
) else (
    echo ❌ .env 파일을 찾을 수 없습니다.
)

REM 3. 프로세스 재시작 안내
echo.
echo 3️⃣ 프로세스 재시작 안내
echo 🖥️ Backend 재시작 ^(필요한 경우^):
echo    cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
echo    python run_server.py
echo.
echo 🌐 Frontend 재시작:
echo    cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\airiss-v4-frontend
echo    npm start
echo.

REM 4. 브라우저 확인 사항
echo 4️⃣ 브라우저에서 확인할 사항:
echo ✅ Frontend URL: http://localhost:3001/analysis
echo ✅ Backend Health: http://localhost:8002/health
echo ✅ API Docs: http://localhost:8002/docs
echo.

REM 5. WebSocket 디버깅 가이드
echo 5️⃣ WebSocket 디버깅 가이드:
echo 🔍 브라우저 개발자 도구 콘솔에서 실행:
echo    // debug_websocket.js 파일 내용을 복사하여 콘솔에 붙여넣기
echo    // 또는 다음 명령 실행:
echo    debugAirissWebSocket.diagnose^(^)
echo.

REM 6. 문제 해결 체크리스트
echo 6️⃣ 문제 해결 체크리스트:
echo [ ] Backend 서버가 포트 8002에서 실행 중
echo [ ] Frontend가 포트 3001에서 실행 중
echo [ ] 방화벽이 포트 8002를 허용
echo [ ] 다른 AIRISS 프로세스가 실행되지 않음
echo [ ] 브라우저 캐시가 삭제됨
echo.

REM 7. 빠른 확인 링크
echo 7️⃣ 빠른 확인 링크:
echo 🌐 Frontend 열기
start http://localhost:3001/analysis

echo 🏥 Backend Health 확인
start http://localhost:8002/health

echo.
echo 🎯 완료! 브라우저에서 WebSocket 연결 상태를 확인하세요.
echo 💡 문제가 지속되면 개발자 도구 콘솔에서 오류 메시지를 확인하세요.

pause
