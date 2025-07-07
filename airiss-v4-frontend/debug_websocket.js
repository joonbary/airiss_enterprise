/**
 * AIRISS WebSocket 연결 디버깅 도구
 * 브라우저 개발자 도구 콘솔에서 실행하여 WebSocket 상태 확인
 */

console.log('🔧 AIRISS WebSocket 디버깅 시작...');
console.log('=' * 50);

// 1. 현재 환경 정보 확인
console.log('📍 현재 페이지:', window.location.href);
console.log('📍 프로토콜:', window.location.protocol);
console.log('📍 호스트:', window.location.host);

// 2. 환경 변수 확인
const apiUrl = process?.env?.REACT_APP_API_URL || 'http://localhost:8002';
const wsUrl = process?.env?.REACT_APP_WS_URL || 'ws://localhost:8002/ws';

console.log('🌐 API URL:', apiUrl);
console.log('🔌 WebSocket URL:', wsUrl);

// 3. WebSocket 연결 테스트
function testWebSocketConnection() {
    console.log('\n🧪 WebSocket 연결 테스트 시작...');
    
    const testClientId = `debug-client-${Date.now()}`;
    const testChannels = 'analysis,alerts';
    const testWsUrl = `${wsUrl}/${testClientId}?channels=${testChannels}`;
    
    console.log('🎯 테스트 URL:', testWsUrl);
    
    const ws = new WebSocket(testWsUrl);
    
    ws.onopen = function(event) {
        console.log('✅ WebSocket 연결 성공!', event);
        
        // Ping 메시지 전송
        const pingMessage = {
            type: 'ping',
            timestamp: new Date().toISOString(),
            client_id: testClientId
        };
        
        ws.send(JSON.stringify(pingMessage));
        console.log('📤 Ping 메시지 전송:', pingMessage);
        
        // 5초 후 연결 종료
        setTimeout(() => {
            ws.close(1000, 'Test completed');
            console.log('🔚 테스트 완료 - 연결 종료');
        }, 5000);
    };
    
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 메시지 수신:', data);
        } catch (e) {
            console.log('📨 원시 메시지 수신:', event.data);
        }
    };
    
    ws.onerror = function(error) {
        console.error('❌ WebSocket 오류:', error);
        console.error('❌ 가능한 원인:');
        console.error('   1. 서버가 실행되지 않음 (포트 8002)');
        console.error('   2. CORS 정책 문제');
        console.error('   3. 네트워크 방화벽');
        console.error('   4. WebSocket 프로토콜 불일치');
    };
    
    ws.onclose = function(event) {
        console.log('🔌 WebSocket 연결 종료:', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
        });
        
        if (event.code !== 1000) {
            console.error('❌ 비정상 종료 감지');
            console.error('❌ 원인 분석:');
            console.error(`   코드: ${event.code}`);
            console.error(`   이유: ${event.reason || '알 수 없음'}`);
        }
    };
    
    // 10초 후에도 연결되지 않으면 강제 종료
    setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
            console.error('⏰ 연결 시간 초과 - 강제 종료');
            ws.close();
        }
    }, 10000);
    
    return ws;
}

// 4. 백엔드 서버 상태 확인
async function checkBackendHealth() {
    console.log('\n🏥 백엔드 서버 상태 확인...');
    
    try {
        const response = await fetch(`${apiUrl}/health`);
        const data = await response.json();
        
        console.log('✅ 백엔드 서버 응답:', data);
        console.log('🔌 WebSocket 관리자 상태:', data.components?.websocket_manager);
        console.log('📊 활성 연결 수:', data.components?.connection_count);
        
        return true;
    } catch (error) {
        console.error('❌ 백엔드 서버 접근 실패:', error);
        console.error('❌ 해결 방법:');
        console.error('   1. 서버가 포트 8002에서 실행 중인지 확인');
        console.error('   2. python run_server.py 실행');
        console.error('   3. uvicorn app.main:app --host 0.0.0.0 --port 8002');
        
        return false;
    }
}

// 5. 종합 진단 실행
async function runComprehensiveDiagnostic() {
    console.log('\n🔍 AIRISS WebSocket 종합 진단 시작...');
    console.log('=' * 50);
    
    // 백엔드 상태 확인
    const backendHealthy = await checkBackendHealth();
    
    if (backendHealthy) {
        console.log('\n✅ 백엔드 서버 정상 - WebSocket 연결 테스트 진행');
        testWebSocketConnection();
    } else {
        console.log('\n❌ 백엔드 서버 문제 - WebSocket 테스트 중단');
    }
    
    // 브라우저 WebSocket 지원 확인
    console.log('\n🌐 브라우저 WebSocket 지원:', !!window.WebSocket);
    
    // 현재 네트워크 상태
    console.log('🌐 온라인 상태:', navigator.onLine);
    
    // 권장 해결 방법
    console.log('\n💡 문제 해결 가이드:');
    console.log('1. 포트 충돌 확인: netstat -ano | findstr :8002');
    console.log('2. 방화벽 설정 확인');
    console.log('3. Frontend 재시작: npm start');
    console.log('4. Backend 재시작: python run_server.py');
    console.log('5. 브라우저 캐시 삭제');
}

// 자동 실행
runComprehensiveDiagnostic();

// 전역 함수로 등록하여 수동 실행 가능
window.debugAirissWebSocket = {
    test: testWebSocketConnection,
    health: checkBackendHealth,
    diagnose: runComprehensiveDiagnostic
};

console.log('\n📝 사용법:');
console.log('- 재진단: debugAirissWebSocket.diagnose()');
console.log('- WebSocket 테스트: debugAirissWebSocket.test()');
console.log('- 서버 상태: debugAirissWebSocket.health()');
