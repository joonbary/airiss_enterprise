#!/bin/bash
# AIRISS WebSocket 문제 긴급 수정 스크립트

echo "🔧 AIRISS WebSocket 긴급 수정 시작..."
echo "=================================="

# 1. Backend 서버 상태 확인
echo "1️⃣ Backend 서버 상태 확인..."
python debug_backend_websocket.py

# 2. Frontend 포트 설정 확인
echo -e "\n2️⃣ Frontend 포트 설정 확인..."
if [ -f "airiss-v4-frontend/.env" ]; then
    echo "📝 현재 .env 설정:"
    cat airiss-v4-frontend/.env | grep PORT
    echo "✅ 포트가 3001로 설정되었습니다."
else
    echo "❌ .env 파일을 찾을 수 없습니다."
fi

# 3. 프로세스 재시작 안내
echo -e "\n3️⃣ 프로세스 재시작 안내"
echo "🖥️ Backend 재시작 (필요한 경우):"
echo "   cd C:\\Users\\apro\\OneDrive\\Desktop\\AIRISS\\airiss_v4"
echo "   python run_server.py"
echo ""
echo "🌐 Frontend 재시작:"
echo "   cd C:\\Users\\apro\\OneDrive\\Desktop\\AIRISS\\airiss_v4\\airiss-v4-frontend"
echo "   npm start"
echo ""

# 4. 브라우저 확인 사항
echo "4️⃣ 브라우저에서 확인할 사항:"
echo "✅ Frontend URL: http://localhost:3001/analysis"
echo "✅ Backend Health: http://localhost:8002/health"
echo "✅ API Docs: http://localhost:8002/docs"
echo ""

# 5. WebSocket 디버깅 가이드
echo "5️⃣ WebSocket 디버깅 가이드:"
echo "🔍 브라우저 개발자 도구 콘솔에서 실행:"
echo "   // 파일 내용 복사 후 실행"
echo "   const script = document.createElement('script');"
echo "   script.src = './debug_websocket.js';"
echo "   document.head.appendChild(script);"
echo ""
echo "📋 또는 수동으로 확인:"
echo "   debugAirissWebSocket.diagnose()"
echo ""

# 6. 문제 해결 체크리스트
echo "6️⃣ 문제 해결 체크리스트:"
echo "[ ] Backend 서버가 포트 8002에서 실행 중"
echo "[ ] Frontend가 포트 3001에서 실행 중"
echo "[ ] 방화벽이 포트 8002를 허용"
echo "[ ] 다른 AIRISS 프로세스가 실행되지 않음"
echo "[ ] 브라우저 캐시가 삭제됨"
echo ""

echo "🎯 완료! 이제 http://localhost:3001/analysis에서 테스트하세요."
