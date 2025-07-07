// Enhanced WebSocket service with better error handling
class SimpleEventEmitter {
  private listeners: { [key: string]: Function[] } = {};

  on(event: string, callback: Function): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  off(event: string, callback: Function): void {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  }

  emit(event: string, ...args: any[]): void {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(...args);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  removeAllListeners(event?: string): void {
    if (event) {
      delete this.listeners[event];
    } else {
      this.listeners = {};
    }
  }
}

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
  type: 'progress' | 'result' | 'complete' | 'error' | 'alert' | 'notification' | 'connection' | 'ready' | 'pong';
  data?: any;
  error?: string;
  message?: string;
  timestamp?: string;
  channel?: string;
  client_id?: string;
  job_id?: string;
}

class EnhancedWebSocketService extends SimpleEventEmitter {
  private ws: WebSocket | null = null;
  private reconnectInterval: number = 5000;
  private maxReconnectAttempts: number = 10;
  private reconnectAttempts: number = 0;
  private reconnectTimer?: NodeJS.Timeout;
  private pingTimer?: NodeJS.Timeout;
  private url: string;
  private clientId: string;
  private isConnecting: boolean = false;
  private shouldReconnect: boolean = true;
  private currentChannels: string[] = [];

  constructor() {
    super();
    this.url = process.env.REACT_APP_WS_URL || 'ws://localhost:8002/ws';
    this.clientId = `react-client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  connect(channels: string[] = ['analysis', 'alerts']): void {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      console.log('🔌 WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    this.currentChannels = channels;
    this.shouldReconnect = true;
    
    const channelsParam = channels.join(',');
    const wsUrl = `${this.url}/${this.clientId}?channels=${channelsParam}`;
    
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
    console.log(`📊 Client ID: ${this.clientId}`);
    console.log(`📡 Channels: ${channels.join(', ')}`);

    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error);
      this.isConnecting = false;
      this.handleReconnection();
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('✅ WebSocket connected successfully');
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected', {
        clientId: this.clientId,
        channels: this.currentChannels
      });
      this.clearReconnectTimer();
      this.startPingInterval();
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('📨 WebSocket message received:', data);
        this.handleMessage(data);
      } catch (error) {
        console.error('❌ WebSocket message parse error:', error, 'Raw data:', event.data);
        this.emit('error', new Error(`Message parse error: ${error}`));
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      this.isConnecting = false;
      
      // 안전한 에러 처리
      const errorMessage = error instanceof Error ? error.message : 'WebSocket connection error';
      const errorEvent = new Error(errorMessage);
      
      this.emit('error', errorEvent);
      
      // 자동 재연결 시도
      if (this.shouldReconnect) {
        this.handleReconnection();
      }
    };

    this.ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });
      
      this.isConnecting = false;
      this.stopPingInterval();
      
      this.emit('disconnected', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      });
      
      // 비정상 종료인 경우에만 재연결 시도
      if (this.shouldReconnect && event.code !== 1000) {
        this.handleReconnection();
      }
    };
  }

  private handleMessage(data: WebSocketMessage): void {
    switch (data.type) {
      case 'ready':
        console.log('🎯 WebSocket ready:', data);
        this.emit('ready', data);
        break;
      case 'connection':
        console.log('🔗 Connection confirmed:', data);
        this.emit('connected', data);
        break;
      case 'progress':
        this.emit('progress', data.data as AnalysisProgress);
        break;
      case 'result':
        this.emit('result', data.data as AnalysisResult);
        break;
      case 'complete':
        this.emit('complete', data.data || data);
        break;
      case 'error':
        console.error('📨 Server error:', data.error || data.message);
        this.emit('serverError', data.error || data.message);
        break;
      case 'alert':
        this.emit('alert', data.data || data);
        break;
      case 'notification':
        this.emit('notification', data.data || data);
        break;
      case 'pong':
        console.log('🏓 Pong received');
        break;
      default:
        console.warn('⚠️ Unknown message type:', data.type);
        this.emit('message', data);
    }
  }

  private handleReconnection(): void {
    if (!this.shouldReconnect || this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('🚫 Max reconnection attempts reached or reconnection disabled');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.clearReconnectTimer();
    this.reconnectAttempts++;
    
    const delay = Math.min(this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1), 30000);
    
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      if (this.shouldReconnect) {
        console.log(`🔄 Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
        this.connect(this.currentChannels);
      }
    }, delay);
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    this.pingTimer = setInterval(() => {
      this.ping();
    }, 30000); // 30초마다 ping
  }

  private stopPingInterval(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = undefined;
    }
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }
  }

  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket');
    this.shouldReconnect = false;
    this.clearReconnectTimer();
    this.stopPingInterval();
    
    if (this.ws) {
      this.ws.close(1000, 'Normal closure');
      this.ws = null;
    }
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  send(data: any): boolean {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        const message = {
          ...data,
          timestamp: new Date().toISOString(),
          client_id: this.clientId
        };
        this.ws.send(JSON.stringify(message));
        console.log('📤 WebSocket message sent:', message);
        return true;
      } catch (error) {
        console.error('❌ Failed to send WebSocket message:', error);
        this.emit('error', error);
        return false;
      }
    } else {
      console.error('❌ WebSocket is not connected. Current state:', this.getConnectionStatus());
      this.emit('error', new Error('WebSocket not connected'));
      return false;
    }
  }

  ping(): void {
    this.send({
      type: 'ping'
    });
  }

  // 분석 시작 알림
  notifyAnalysisStart(jobId: string): void {
    this.send({
      type: 'analysis_start',
      jobId,
      message: 'Analysis started'
    });
  }

  // 채널 구독
  subscribeToChannel(channel: string): void {
    this.send({
      type: 'subscribe',
      channel
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

  // 재연결 활성화/비활성화
  enableReconnect(): void {
    this.shouldReconnect = true;
  }

  disableReconnect(): void {
    this.shouldReconnect = false;
  }

  // 클라이언트 ID 반환
  getClientId(): string {
    return this.clientId;
  }

  // 현재 채널 목록 반환
  getCurrentChannels(): string[] {
    return [...this.currentChannels];
  }

  // 연결 통계
  getConnectionStats() {
    return {
      clientId: this.clientId,
      status: this.getConnectionStatus(),
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      shouldReconnect: this.shouldReconnect,
      channels: this.currentChannels
    };
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
const websocketService = new EnhancedWebSocketService();

// 전역 에러 핸들러 추가
websocketService.on('error', (error: Error) => {
  console.error('🚨 WebSocket Service Error:', error?.message || 'Unknown error');
});

export default websocketService;
