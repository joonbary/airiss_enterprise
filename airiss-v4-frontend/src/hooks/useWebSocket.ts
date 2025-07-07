import { useState, useEffect, useCallback, useRef } from 'react';
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
}

export const useWebSocket = (): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  
  const isInitialized = useRef(false);

  // 이벤트 핸들러들
  const handleConnected = useCallback(() => {
    console.log('🎉 WebSocket connected via hook');
    setIsConnected(true);
    setConnectionStatus('connected');
  }, []);

  const handleDisconnected = useCallback(() => {
    console.log('💔 WebSocket disconnected via hook');
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const handleProgress = useCallback((progressData: AnalysisProgress) => {
    console.log('📊 Progress update:', progressData);
    setProgress(progressData);
  }, []);

  const handleResult = useCallback((result: AnalysisResult) => {
    console.log('🎯 New result:', result);
    setResults(prev => [...prev, result]);
  }, []);

  const handleComplete = useCallback((data: any) => {
    console.log('✅ Analysis complete:', data);
    setProgress((prev: AnalysisProgress | null) => prev ? { ...prev, status: 'completed', progress: 100 } : null);
  }, []);

  const handleError = useCallback((error: any) => {
    // error가 객체/문자열/undefined 모두 안전하게 처리
    let errorMsg = '알 수 없는 WebSocket 오류';
    if (error) {
      if (typeof error === 'string') errorMsg = error;
      else if (error.message) errorMsg = error.message;
      else errorMsg = JSON.stringify(error);
    }
    console.error('❌ WebSocket error via hook:', errorMsg, error);
    setProgress((prev: AnalysisProgress | null) => prev ? { ...prev, status: 'failed', error: errorMsg } : null);
  }, []);

  const handleAlert = useCallback((alert: any) => {
    console.log('🚨 Alert received:', alert);
    setAlerts(prev => [{ ...alert, timestamp: new Date().toISOString() }, ...prev]);
  }, []);

  const handleNotification = useCallback((notification: any) => {
    console.log('🔔 Notification received:', notification);
    setNotifications(prev => [{ ...notification, timestamp: new Date().toISOString() }, ...prev]);
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    console.log('📬 Generic message received:', message);
  }, []);

  // WebSocket 연결 및 이벤트 리스너 설정
  useEffect(() => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    // 이벤트 리스너 등록
    webSocketService.on('connected', handleConnected);
    webSocketService.on('disconnected', handleDisconnected);
    webSocketService.on('progress', handleProgress);
    webSocketService.on('result', handleResult);
    webSocketService.on('complete', handleComplete);
    webSocketService.on('error', handleError);
    webSocketService.on('alert', handleAlert);
    webSocketService.on('notification', handleNotification);
    webSocketService.on('message', handleMessage);

    // 초기 연결 상태 설정
    setIsConnected(webSocketService.isConnected());
    setConnectionStatus(webSocketService.getConnectionStatus());

    // 클린업 함수
    return () => {
      webSocketService.removeListener('connected', handleConnected);
      webSocketService.removeListener('disconnected', handleDisconnected);
      webSocketService.removeListener('progress', handleProgress);
      webSocketService.removeListener('result', handleResult);
      webSocketService.removeListener('complete', handleComplete);
      webSocketService.removeListener('error', handleError);
      webSocketService.removeListener('alert', handleAlert);
      webSocketService.removeListener('notification', handleNotification);
      webSocketService.removeListener('message', handleMessage);
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
    handleMessage
  ]);

  // 연결 함수
  const connect = useCallback((channels: string[] = ['analysis', 'alerts']) => {
    console.log('🔌 Connecting with channels:', channels);
    webSocketService.connect(channels);
  }, []);

  // 연결 해제 함수
  const disconnect = useCallback(() => {
    console.log('🔌 Disconnecting...');
    webSocketService.disconnect();
  }, []);

  // 메시지 전송 함수
  const sendMessage = useCallback((data: any): boolean => {
    return webSocketService.send(data);
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
    clearNotifications
  };
};

export default useWebSocket;