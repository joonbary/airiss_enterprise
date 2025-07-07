import { EventEmitter } from 'events';

// WebSocket 디버깅 스크립트 - 브라우저 콘솔에서 실행
console.log('🔧 AIRISS WebSocket 디버깅 시작...');

export type AnalysisProgress = {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  currentEmployee?: string;
  message?: string;
  error?: string;
};

export type AnalysisResult = {
  uid: string;
  overall_score: number;
  grade: string;
  dimension_scores: Record<string, number>;
};

export type WebSocketMessage = {
  type:
    | 'progress'
    | 'result'
    | 'complete'
    | 'error'
    | 'alert'
    | 'notification'
    | 'connection_established'
    | 'pong';
  data?: any;
  error?: string;
  timestamp?: string;
};

// 1. 현재 서버 상태 확인
async function checkServerStatus() {
    console.log('\n🏥 서버 상태 확인 중...');
    
    const apiUrl = 'http://localhost:8002';
    const wsUrl = 'ws://localhost:8002/ws';
    
    try {
        // API 서버 확인
        const response = await fetch(`${apiUrl}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ 백엔드 서버 정상:', data);
            return true;
        } else {
            console.log('❌ 백엔드 서버 응답 오류:', response.status);
            return false;
        }
    } catch (error) {
        if (error && error instanceof Error) {
            console.log('❌ 백엔드 서버 연결 실패:', error.message);
        } else {
            console.log('❌ 백엔드 서버 연결 실패:', String(error));
        }
        console.log('💡 해결 방법:');
        console.log('   1. 터미널에서 프로젝트 폴더로 이동');
        console.log('   2. python run_server.py 실행');
        console.log('   3. 또는 uvicorn app.main:app --host 0.0.0.0 --port 8002');
        return false;
    }
}

// 2. WebSocket 연결 테스트
function testWebSocketConnection() {
    console.log('\n🔌 WebSocket 연결 테스트...');
    
    const clientId = `debug-${Date.now()}`;
    const wsUrl = `ws://localhost:8002/ws/${clientId}?channels=analysis,alerts`;
    
    console.log('🎯 연결 URL:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    
    const connectionTimeout = setTimeout(() => {
        console.log('⏰ 연결 시간 초과 (10초)');
        ws.close();
    }, 10000);
    
    ws.onopen = () => {
        console.log('✅ WebSocket 연결 성공!');
        clearTimeout(connectionTimeout);
        
        // Ping 테스트
        ws.send(JSON.stringify({
            type: 'ping',
            timestamp: new Date().toISOString()
        }));
        
        // 5초 후 연결 종료
        setTimeout(() => {
            ws.close(1000, 'Test completed');
        }, 5000);
    };
    
    ws.onmessage = (event) => {
        console.log('📨 메시지 수신:', JSON.parse(event.data));
    };
    
    ws.onerror = (error) => {
        console.log('❌ WebSocket 연결 오류:', error);
        clearTimeout(connectionTimeout);
    };
    
    ws.onclose = (event) => {
        console.log('🔌 연결 종료:', {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean
        });
        clearTimeout(connectionTimeout);
    };
    
    return ws;
}

// 3. 포트 사용 상태 확인
function checkPortStatus() {
    console.log('\n🔍 포트 사용 상태 확인...');
    console.log('현재 페이지 URL:', window.location.href);
    console.log('예상 포트:');
    console.log('  - 프론트엔드: 3001');
    console.log('  - 백엔드: 8002');
    
    // 네트워크 상태
    console.log('네트워크 상태:', navigator.onLine ? '온라인' : '오프라인');
}

// 4. 오류 로그 캡처
function captureErrorLogs() {
    console.log('\n📝 오류 로그 캡처 설정...');
    
    // WebSocket 관련 전역 오류 캐치
    const originalError = window.onerror;
    window.onerror = function(message, source, lineno, colno, error) {
        if (typeof message === 'string' && message.includes('WebSocket')) {
            console.error('🚨 WebSocket 관련 오류 감지:', {
                message, source, lineno, colno, error
            });
        }
        if (typeof source === 'string' && source && source.includes('websocket')) {
            console.error('🚨 WebSocket 관련 오류 감지:', {
                message, source, lineno, colno, error
            });
        }
        if (error && error instanceof Error) {
            console.error('🚨 WebSocket 관련 오류 감지:', {
                message: error.message,
                stack: error.stack,
                error: error
            });
        } else if (error) {
            console.error('🚨 WebSocket 관련 오류 감지:', {
                message: String(error),
                error: error
            });
        }
        if (originalError) {
            return originalError.apply(this, arguments as any);
        }
    };
    
    // unhandledrejection 이벤트 캐치
    window.addEventListener('unhandledrejection', (event) => {
        if (event.reason?.message?.includes('WebSocket')) {
            console.error('🚨 WebSocket Promise 거부:', event.reason);
            event.preventDefault(); // 오류 방지
        }
    });
    
    console.log('✅ 오류 캡처 설정 완료');
}

// 5. 종합 진단 실행
async function runDiagnosis() {
    console.log('🔍 AIRISS WebSocket 종합 진단 시작...');
    console.log('='.repeat(50));
    
    // 오류 캡처 설정
    captureErrorLogs();
    
    // 포트 상태 확인
    checkPortStatus();
    
    // 서버 상태 확인
    const serverOk = await checkServerStatus();
    
    if (serverOk) {
        // WebSocket 테스트
        testWebSocketConnection();
    }
    
    console.log('\n💡 문제 해결 체크리스트:');
    console.log('□ 백엔드 서버 실행 (python run_server.py)');
    console.log('□ 포트 8002 사용 가능 여부 확인');
    console.log('□ 방화벽/바이러스 프로그램 확인');
    console.log('□ 브라우저 캐시 삭제');
    console.log('□ 다른 브라우저에서 테스트');
    
    console.log('\n🔧 수동 명령어:');
    console.log('- 재진단: runDiagnosis()');
    console.log('- 서버 확인: checkServerStatus()');
    console.log('- WebSocket 테스트: testWebSocketConnection()');
}

// 전역 함수로 등록
(window as any).debugWebSocket = {
    diagnose: runDiagnosis,
    checkServer: checkServerStatus,
    testConnection: testWebSocketConnection,
    checkPorts: checkPortStatus
};

// 자동 실행
runDiagnosis();

class WebSocketService extends EventEmitter {
  private connected = false;
  private connectionStatus = 'disconnected';

  isConnected() {
    return this.connected;
  }

  getConnectionStatus() {
    return this.connectionStatus;
  }

  connect(channels: string[] = []) {
    this.connected = true;
    this.connectionStatus = 'connected';
    this.emit('connected');
  }

  disconnect() {
    this.connected = false;
    this.connectionStatus = 'disconnected';
    this.emit('disconnected');
  }

  send(data: any) {
    this.emit('message', { type: 'sent', data });
    return true;
  }

  forceReconnect() {
    this.disconnect();
    setTimeout(() => this.connect(), 1000);
  }

  getStatus() {
    return {
      isConnected: this.connected,
      connectionStatus: this.connectionStatus,
    };
  }

  async testConnection() {
    return this.connected;
  }
}

export default new WebSocketService();