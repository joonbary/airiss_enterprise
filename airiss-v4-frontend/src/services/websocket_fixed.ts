import { EventEmitter } from 'events';

export interface AnalysisProgress {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processed: number;
  total: number;
  currentEmployee?: string;
  message?: string;
  error?: string;
}

export interface AnalysisResult {
  uid: string;
  overall_score: number;
  grade: string;
  dimension_scores: Record<string, number>;
}

export interface WebSocketMessage {
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
}

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private reconnectTimer?: NodeJS.Timeout;
  private url: string;
  private clientId: string;
  private isConnecting: boolean = false;
  private maxRetryAttempts: number = 3;
  private retryCount: number = 0;

  constructor() {
    super();
    this.url = process.env.REACT_APP_WS_URL || 'ws://localhost:8002/ws';
    this.clientId = `react-client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // EventEmitter 오류 처리 추가
    this.on('error', (error) => {
      console.error('WebSocketService Error:', error);
      // 오류가 처리되었음을 명시적으로 표시
    });
  }

  connect(channels: string[] = ['analysis', 'alerts']): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      console.log('🔌 WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    const channelsParam = channels.join(',');
    const wsUrl = `${this.url}/${this.clientId}?channels=${channelsParam}`;
    
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupWebSocketHandlers(channels);
    } catch (error) {
      console.error('❌ WebSocket creation failed:', error);
      this.handleConnectionError('WebSocket creation failed', channels);
    }
  }

  private setupWebSocketHandlers(channels: string[]): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected successfully');
      this.isConnecting = false;
      this.retryCount = 0; // 성공 시 재시도 카운트 리셋
      this.emit('connected');
      this.clearReconnectTimer();
      
      // 연결 확인 메시지 전송
      this.send({
        type: 'ping',
        timestamp: new Date().toISOString()
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('📨 WebSocket message received:', data);
        this.handleMessage(data);
      } catch (error) {
        console.error('❌ WebSocket message parse error:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error occurred:', error);
      
      // 오류 객체를 안전하게 처리
      const errorInfo = {
        message: 'WebSocket connection error',
        type: 'websocket_error',
        timestamp: new Date().toISOString(),
        readyState: this.ws?.readyState,
        url: this.url
      };

      // 직접 emit하지 말고 비동기로 처리
      setTimeout(() => {
        this.handleConnectionError(errorInfo.message, channels);
      }, 0);
    };

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });
      
      this.isConnecting = false;
      this.emit('disconnected');
      
      // 비정상 종료 시 재연결 시도
      if (event.code !== 1000 && this.retryCount < this.maxRetryAttempts) {
        this.scheduleReconnect(channels);
      } else if (this.retryCount >= this.maxRetryAttempts) {
        console.error('❌ Max retry attempts reached. Please check server status.');
        this.emit('maxRetriesReached');
      }
    };
  }

  private handleConnectionError(message: string, channels: string[]): void {
    this.isConnecting = false;
    this.retryCount++;
    
    console.error(`❌ Connection error (attempt ${this.retryCount}/${this.maxRetryAttempts}):`, message);
    
    // 안전한 오류 객체 생성
    const safeErrorInfo = {
      message,
      type: 'connection_error',
      attempt: this.retryCount,
      maxAttempts: this.maxRetryAttempts,
      timestamp: new Date().toISOString()
    };

    // emit 대신 console.error 사용하거나 try-catch로 감싸기
    try {
      this.emit('error', safeErrorInfo);
    } catch (emitError) {
      console.error('❌ Error emitting error event:', emitError);
    }

    // 재시도 가능한 경우 재연결 스케줄링
    if (this.retryCount < this.maxRetryAttempts) {
      this.scheduleReconnect(channels);
    }
  }

  private handleMessage(data: WebSocketMessage): void {
    switch (data.type) {
      case 'progress':
        this.emit('progress', data.data as AnalysisProgress);
        break;
      case 'result':
        this.emit('result', data.data as AnalysisResult);
        break;
      case 'complete':
        this.emit('complete', data.data);
        break;
      case 'error':
        this.emit('error', { message: data.error, type: 'server_error' });
        break;
      case 'alert':
        this.emit('alert', data.data);
        break;
      case 'notification':
        this.emit('notification', data.data);
        break;
      case 'connection_established':
      case 'pong':
        console.log('ℹ️ WebSocket keepalive/control message:', data.type);
        break;
      default:
        console.warn('⚠️ Unknown message type:', data.type);
        break;
    }
  }

  private scheduleReconnect(channels: string[]): void {
    this.clearReconnectTimer();
    const delay = this.reconnectInterval * Math.pow(2, this.retryCount - 1); // Exponential backoff
    
    console.log(`🔄 Scheduling reconnect in ${delay}ms (attempt ${this.retryCount + 1}/${this.maxRetryAttempts})`);
    
    this.reconnectTimer = setTimeout(() => {
      if (this.retryCount < this.maxRetryAttempts) {
        console.log('🔄 Attempting to reconnect...');
        this.connect(channels);
      }
    }, delay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
  }

  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket');
    this.clearReconnectTimer();
    this.retryCount = this.maxRetryAttempts; // 재연결 방지
    if (this.ws) {
      this.ws.close(1000, 'Normal closure');
      this.ws = null;
    }
    this.isConnecting = false;
  }

  send(data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const message = {
          ...data,
          timestamp: new Date().toISOString()
        };
        this.ws.send(JSON.stringify(message));
        console.log('📤 WebSocket message sent:', message);
        return true;
      } catch (error) {
        console.error('❌ Failed to send WebSocket message:', error);
        return false;
      }
    } else {
      console.error('❌ WebSocket is not connected. Current state:', this.getConnectionStatus());
      return false;
    }
  }

  // 분석 시작 알림
  notifyAnalysisStart(jobId: string): void {
    this.send({
      type: 'analysis_start',
      jobId,
      message: 'Analysis started'
    });
  }

  // 연결 상태 확인
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // 연결 상태 문자열
  getConnectionStatus(): string {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }

  // 재시도 카운트 리셋 (수동 재연결용)
  resetRetryCount(): void {
    this.retryCount = 0;
  }

  // 서버 상태 확인
  async checkServerHealth(): Promise<boolean> {
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8002';
      const response = await fetch(`${apiUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
export default new WebSocketService();