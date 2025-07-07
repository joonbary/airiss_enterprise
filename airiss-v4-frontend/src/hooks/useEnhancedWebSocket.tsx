// WebSocket 서비스 사용 예시 (컴포넌트에서 활용)
import React, { useEffect, useState, useCallback } from 'react';
// 기존 서비스 대신 새로운 향상된 서비스 사용
import websocketService from '../services/websocket_enhanced';

interface WebSocketStatusProps {
  onConnectionChange?: (connected: boolean) => void;
}

const useEnhancedWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // 연결 상태 리스너
    const handleConnected = (data: any) => {
      console.log('✅ WebSocket Connected:', data);
      setIsConnected(true);
      setConnectionStatus('connected');
      setError(null);
    };

    const handleDisconnected = (data: any) => {
      console.log('🔌 WebSocket Disconnected:', data);
      setIsConnected(false);
      setConnectionStatus('disconnected');
    };

    const handleReady = (data: any) => {
      console.log('🎯 WebSocket Ready:', data);
      setConnectionStatus('ready');
    };

    const handleError = (error: Error) => {
      console.error('❌ WebSocket Error:', error);
      setError(error.message);
      setIsConnected(false);
    };

    const handleProgress = (data: any) => {
      console.log('📊 Analysis Progress:', data);
      setLastMessage({ type: 'progress', data });
    };

    const handleResult = (data: any) => {
      console.log('✨ Analysis Result:', data);
      setLastMessage({ type: 'result', data });
    };

    const handleComplete = (data: any) => {
      console.log('🎉 Analysis Complete:', data);
      setLastMessage({ type: 'complete', data });
    };

    const handleAlert = (data: any) => {
      console.log('🚨 Alert:', data);
      setLastMessage({ type: 'alert', data });
    };

    const handleServerError = (error: string) => {
      console.error('🚨 Server Error:', error);
      setError(error);
    };

    // 이벤트 리스너 등록
    websocketService.on('connected', handleConnected);
    websocketService.on('disconnected', handleDisconnected);
    websocketService.on('ready', handleReady);
    websocketService.on('error', handleError);
    websocketService.on('progress', handleProgress);
    websocketService.on('result', handleResult);
    websocketService.on('complete', handleComplete);
    websocketService.on('alert', handleAlert);
    websocketService.on('serverError', handleServerError);

    // WebSocket 연결 시작
    websocketService.connect(['analysis', 'alerts', 'notifications']);

    // 클린업
    return () => {
      websocketService.off('connected', handleConnected);
      websocketService.off('disconnected', handleDisconnected);
      websocketService.off('ready', handleReady);
      websocketService.off('error', handleError);
      websocketService.off('progress', handleProgress);
      websocketService.off('result', handleResult);
      websocketService.off('complete', handleComplete);
      websocketService.off('alert', handleAlert);
      websocketService.off('serverError', handleServerError);
    };
  }, []);

  // WebSocket 상태 확인
  const checkConnection = useCallback(() => {
    const status = websocketService.getConnectionStatus();
    const stats = websocketService.getConnectionStats();
    setConnectionStatus(status);
    setIsConnected(websocketService.isConnected());
    
    console.log('📊 WebSocket Stats:', stats);
    return { status, stats };
  }, []);

  // 수동 재연결
  const reconnect = useCallback(() => {
    console.log('🔄 Manual reconnect requested');
    websocketService.disconnect();
    setTimeout(() => {
      websocketService.connect(['analysis', 'alerts', 'notifications']);
    }, 1000);
  }, []);

  // 메시지 전송
  const sendMessage = useCallback((message: any) => {
    return websocketService.send(message);
  }, []);

  return {
    isConnected,
    connectionStatus,
    lastMessage,
    error,
    checkConnection,
    reconnect,
    sendMessage,
    clientId: websocketService.getClientId()
  };
};

// WebSocket 상태 표시 컴포넌트
export const WebSocketStatus: React.FC<WebSocketStatusProps> = ({ onConnectionChange }) => {
  const { 
    isConnected, 
    connectionStatus, 
    error, 
    checkConnection, 
    reconnect, 
    clientId 
  } = useEnhancedWebSocket();

  useEffect(() => {
    if (onConnectionChange) {
      onConnectionChange(isConnected);
    }
  }, [isConnected, onConnectionChange]);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
      case 'ready':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'disconnected':
      case 'closed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
      case 'ready':
        return '🟢';
      case 'connecting':
        return '🟡';
      case 'disconnected':
      case 'closed':
        return '🔴';
      default:
        return '⚪';
    }
  };

  return (
    <div className="flex items-center space-x-3 p-3 bg-white rounded-lg shadow-sm border">
      <div className="flex items-center space-x-2">
        <span className="text-lg">{getStatusIcon()}</span>
        <span className={`font-medium ${getStatusColor()}`}>
          {connectionStatus.toUpperCase()}
        </span>
      </div>
      
      {error && (
        <div className="text-red-500 text-sm">
          ❌ {error}
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        ID: {clientId.slice(-8)}
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={checkConnection}
          className="px-3 py-1 text-xs bg-blue-100 text-blue-600 rounded hover:bg-blue-200"
        >
          상태확인
        </button>
        
        {!isConnected && (
          <button
            onClick={reconnect}
            className="px-3 py-1 text-xs bg-green-100 text-green-600 rounded hover:bg-green-200"
          >
            재연결
          </button>
        )}
      </div>
    </div>
  );
};

// 파일 업로드 시 WebSocket 연동 예시
export const useFileUploadWithWebSocket = () => {
  const { sendMessage } = useEnhancedWebSocket();

  const uploadFile = useCallback(async (file: File) => {
    try {
      // 파일 업로드 시작 알림
      sendMessage({
        type: 'upload_start',
        fileName: file.name,
        fileSize: file.size
      });

      // 실제 파일 업로드 로직
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('파일 업로드 실패');
      }

      const result = await response.json();
      
      // 업로드 완료 알림
      sendMessage({
        type: 'upload_complete',
        fileId: result.file_id,
        fileName: file.name
      });

      return result;
    } catch (error) {
      // 업로드 실패 알림
      sendMessage({
        type: 'upload_error',
        error: error instanceof Error ? error.message : '알 수 없는 오류'
      });
      throw error;
    }
  }, [sendMessage]);

  return { uploadFile };
};

export default useEnhancedWebSocket;
