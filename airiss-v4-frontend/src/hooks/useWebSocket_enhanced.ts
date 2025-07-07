import { useState, useEffect, useCallback, useRef } from 'react';
// 기존 websocket 대신 robust 버전 사용 (문제 해결되지 않을 경우만)
// import webSocketService from '../services/websocket';
import webSocketService, { AnalysisProgress, AnalysisResult, WebSocketMessage } from '../services/websocket';

export interface UseWebSocketReturn {
  isConnected: boolean;
  connectionStatus: string;
  progress: AnalysisProgress | null;
  results: AnalysisResult[];
  alerts: any[];
  notifications: any[];
  connect: (channels?: string[]) => void;
  disconnect: () => void;
  sendMessage: (data: any) => boolean;
  clearResults: () => void;
  clearAlerts: () => void;
  clearNotifications: () => void;
  // 추가된 디버깅 기능
  forceReconnect: () => void;
  getStatus: () => any;
  testConnection: () => Promise<boolean>;
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  
  const isInitialized = useRef(false);

  // 향상된 이벤트 핸들러들
  const handleConnected = useCallback(() => {
    console.log('🎉 WebSocket connected via enhanced hook');
    setIsConnected(true);
    setConnectionStatus('connected');
  }, []);

  const handleDisconnected = useCallback((event?: any) => {
    console.log('💔 WebSocket disconnected via enhanced hook', event);
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const handleProgress = useCallback((progressData: AnalysisProgress) => {
    console.log('📊 Progress update via enhanced hook:', progressData);
    setProgress(progressData);
  }, []);

  const handleResult = useCallback((result: AnalysisResult) => {
    console.log('🎯 New result via enhanced hook:', result);
    setResults(prev => [...prev, result]);
  }, []);

  const handleComplete = useCallback((data: any) => {
    console.log('✅ Analysis complete via enhanced hook:', data);
    setProgress((prev: AnalysisProgress | null) => prev ? { ...prev, status: 'completed', progress: 100 } : null);
  }, []);

  const handleError = useCallback((error: any) => {
    // 안전한 에러 처리
    let errorMsg = '알 수 없는 WebSocket 오류';
    if (error) {
      if (typeof error === 'string') errorMsg = error;
      else if (error.message) errorMsg = error.message;
      else if (error.details) errorMsg = JSON.stringify(error.details);
      else errorMsg = JSON.stringify(error);
    }
    console.error('❌ WebSocket error via enhanced hook:', errorMsg, error);
    setProgress((prev: AnalysisProgress | null) => prev ? { ...prev, status: 'failed', error: errorMsg } : null);
  }, []);

  const handleAlert = useCallback((alert: any) => {
    console.log('🚨 Alert received via enhanced hook:', alert);
    setAlerts(prev => [{ ...alert, timestamp: new Date().toISOString() }, ...prev]);
  }, []);

  const handleNotification = useCallback((notification: any) => {
    console.log('🔔 Notification received via enhanced hook:', notification);
    setNotifications(prev => [{ ...notification, timestamp: new Date().toISOString() }, ...prev]);
  }, []);

  const handleReady = useCallback((data: any) => {
    console.log('🎯 WebSocket ready via enhanced hook:', data);
    setConnectionStatus('ready');
  }, []);

  const handleMaxReconnectAttempts = useCallback(() => {
    console.error('💔 Max reconnect attempts reached');
    setConnectionStatus('failed');
  }, []);

  // WebSocket 연결 및 이벤트 리스너 설정
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    console.log('🔌 Enhanced useWebSocket 초기화...');

    // 기존 이벤트 리스너 등록
    webSocketService.on('connected', handleConnected);
    webSocketService.on('disconnected', handleDisconnected);
    webSocketService.on('progress', handleProgress);
    webSocketService.on('result', handleResult);
    webSocketService.on('complete', handleComplete);
    webSocketService.on('error', handleError);
    webSocketService.on('alert', handleAlert);
    webSocketService.on('notification', handleNotification);
    
    // 추가된 이벤트 리스너
    webSocketService.on('ready', handleReady);
    webSocketService.on('maxReconnectAttemptsReached', handleMaxReconnectAttempts);

    // 초기 연결 상태 설정
    setIsConnected(webSocketService.isConnected());
    setConnectionStatus(webSocketService.getConnectionStatus());

    // 상태 정보 로깅
    if (webSocketService.getStatus) {
      console.log('📊 WebSocket 초기 상태:', webSocketService.getStatus());
    }

    // 클린업 함수
    return () => {
      console.log('🧹 Enhanced useWebSocket 클린업...');
      
      webSocketService.removeListener('connected', handleConnected);
      webSocketService.removeListener('disconnected', handleDisconnected);
      webSocketService.removeListener('progress', handleProgress);
      webSocketService.removeListener('result', handleResult);
      webSocketService.removeListener('complete', handleComplete);
      webSocketService.removeListener('error', handleError);
      webSocketService.removeListener('alert', handleAlert);
      webSocketService.removeListener('notification', handleNotification);
      webSocketService.removeListener('ready', handleReady);
      webSocketService.removeListener('maxReconnectAttemptsReached', handleMaxReconnectAttempts);
    };
  }, [
    handleConnected,
    handleDisconnected,
    handleProgress,
    handleResult,
    handleComplete,
    handleError,
    handleAlert,
    handleNotification,
    handleReady,
    handleMaxReconnectAttempts
  ]);

  // 연결 함수 (향상됨)
  const connect = useCallback((channels: string[] = ['analysis', 'alerts']) => {
    console.log('🔌 Enhanced connecting with channels:', channels);
    try {
      webSocketService.connect(channels);
    } catch (error) {
      console.error('❌ Enhanced connect failed:', error);
      handleError(error);
    }
  }, [handleError]);

  // 연결 해제 함수
  const disconnect = useCallback(() => {
    console.log('🔌 Enhanced disconnecting...');
    webSocketService.disconnect();
  }, []);

  // 메시지 전송 함수 (향상됨)
  const sendMessage = useCallback((data: any): boolean => {
    try {
      const success = webSocketService.send(data);
      if (!success) {
        console.warn('⚠️ Enhanced sendMessage 실패, 재연결 시도 중...');
      }
      return success;
    } catch (error) {
      console.error('❌ Enhanced sendMessage 오류:', error);
      handleError(error);
      return false;
    }
  }, [handleError]);

  // 강제 재연결 (새로 추가)
  const forceReconnect = useCallback(() => {
    console.log('🔄 Enhanced 강제 재연결...');
    if (webSocketService.forceReconnect) {
      webSocketService.forceReconnect();
    } else {
      // 폴백: 기본 재연결
      disconnect();
      setTimeout(() => connect(), 1000);
    }
  }, [connect, disconnect]);

  // 상태 정보 반환 (새로 추가)
  const getStatus = useCallback(() => {
    if (webSocketService.getStatus) {
      return webSocketService.getStatus();
    }
    return {
      isConnected: isConnected,
      connectionStatus: connectionStatus,
      basic: true
    };
  }, [isConnected, connectionStatus]);

  // 연결 테스트 (새로 추가)
  const testConnection = useCallback(async (): Promise<boolean> => {
    console.log('🧪 Enhanced 연결 테스트 시작...');
    
    if (webSocketService.testConnection) {
      return await webSocketService.testConnection();
    }
    
    // 폴백: 기본 연결 상태 확인
    return webSocketService.isConnected();
  }, []);

  // 상태 초기화 함수들
  const clearResults = useCallback(() => {
    setResults([]);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    isConnected,
    connectionStatus,
    progress,
    results,
    alerts,
    notifications,
    connect,
    disconnect,
    sendMessage,
    clearResults,
    clearAlerts,
    clearNotifications,
    // 새로 추가된 기능들
    forceReconnect,
    getStatus,
    testConnection
  };
};

export default useWebSocket;
