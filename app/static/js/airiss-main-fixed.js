// AIRISS v4.1 Enhanced JavaScript - WebSocket 연결 안정성 개선

// 전역 변수
let selectedFile = null;
let currentJobId = null;
let ws = null;
let debugMode = false;
let resultsChart = null;
let tourStep = 0;
let lastAnalysisResult = null;

// 🔌 WebSocket 연결 개선 변수
let wsReconnectAttempts = 0;
let wsMaxReconnectAttempts = 10;
let wsReconnectDelay = 1000; // 초기 1초
let wsConnectionState = 'disconnected'; // disconnected, connecting, connected
let wsHeartbeatInterval = null;

// 샘플 분석 결과 데이터 (테스트용)
const sampleAnalysisResults = {
    labels: ['업무성과', 'KPI달성', '태도', '커뮤니케이션', '리더십', '협업', '전문성', '창의혁신'],
    datasets: [{
        label: '평균 점수',
        data: [85, 78, 92, 76, 88, 94, 82, 75],
        backgroundColor: 'rgba(255, 87, 34, 0.2)',
        borderColor: 'rgba(255, 87, 34, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(255, 87, 34, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6
    }]
};

// 🎨 향상된 디버깅 시스템
function addDebugLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const debugLog = document.getElementById('debugLog');
    
    // debugLog가 없으면 콘솔에만 출력
    if (!debugLog) {
        console.log(`[AIRISS v4.1 Enhanced] ${type.toUpperCase()}: ${message}`);
        return;
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = 'debug-entry';
    
    const iconMap = {
        'info': 'fas fa-info-circle',
        'success': 'fas fa-check-circle',
        'warning': 'fas fa-exclamation-triangle',
        'error': 'fas fa-times-circle'
    };
    
    const colorMap = {
        'info': '#4CAF50',
        'success': '#4CAF50', 
        'warning': '#FF9800',
        'error': '#f44336'
    };
    
    logEntry.innerHTML = `
        <span class="debug-time">[${timestamp}]</span>
        <i class="${iconMap[type] || iconMap.info}" style="color: ${colorMap[type] || colorMap.info}"></i>
        <span style="margin-left: 8px;">${message}</span>
    `;
    
    debugLog.appendChild(logEntry);
    debugLog.scrollTop = debugLog.scrollHeight;
    
    // 콘솔에도 출력
    console.log(`[AIRISS v4.1 Enhanced] ${type.toUpperCase()}: ${message}`);
}

function toggleDebugInfo() {
    const debugInfo = document.getElementById('debugInfo');
    debugMode = !debugMode;
    if (debugMode) {
        debugInfo.classList.add('show');
        addDebugLog('디버깅 모드 활성화됨', 'success');
    } else {
        debugInfo.classList.remove('show');
    }
}

// 🎯 온보딩 시스템
function showOnboarding() {
    document.getElementById('onboardingOverlay').style.display = 'flex';
}

function skipTour() {
    document.getElementById('onboardingOverlay').style.display = 'none';
    addDebugLog('사용자가 온보딩 투어를 건너뛰었습니다', 'info');
}

function startTour() {
    document.getElementById('onboardingOverlay').style.display = 'none';
    tourStep = 0;
    nextTourStep();
}

function nextTourStep() {
    const steps = [
        { selector: '.upload-area', message: '여기에 Excel 또는 CSV 파일을 업로드하세요' },
        { selector: '#analyzeBtn', message: '파일 업로드 후 이 버튼으로 AI 분석을 시작합니다' },
        { selector: '.progress-container', message: '분석 진행률을 실시간으로 확인할 수 있습니다' },
        { selector: '.features-grid', message: 'AIRISS는 8개 핵심 영역을 종합 분석합니다' }
    ];
    
    if (tourStep < steps.length) {
        const step = steps[tourStep];
        highlightElement(step.selector, step.message);
        tourStep++;
        setTimeout(nextTourStep, 3000);
    } else {
        addDebugLog('온보딩 투어 완료', 'success');
        showNotification('온보딩 투어가 완료되었습니다! 이제 파일을 업로드하여 분석을 시작해보세요.', 'success');
    }
}

function highlightElement(selector, message) {
    const element = document.querySelector(selector);
    if (element) {
        element.style.boxShadow = '0 0 20px rgba(255, 87, 34, 0.8)';
        element.style.transform = 'scale(1.05)';
        
        setTimeout(() => {
            element.style.boxShadow = '';
            element.style.transform = '';
        }, 2500);
        
        showNotification(message, 'info');
        addDebugLog(`투어 단계 ${tourStep + 1}: ${message}`, 'info');
    }
}

// 🔔 향상된 알림 시스템
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const text = document.getElementById('notificationText');
    const icon = document.getElementById('notificationIcon');
    
    // DOM 요소가 없으면 콘솔에만 출력
    if (!notification || !text || !icon) {
        console.log(`[AIRISS v4.1] Notification (${type}): ${message}`);
        return;
    }
    
    const iconMap = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-times-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    text.textContent = message;
    icon.className = iconMap[type] || iconMap.success;
    notification.className = 'notification ' + type + ' show';
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 5000);
    
    addDebugLog(`알림: ${message}`, type);
}

// 🌐 WebSocket 연결 시스템 - 안정성 대폭 개선
function getWebSocketURL() {
    // 🔧 개선: 올바른 WebSocket URL 구성
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    // 🔧 포트 설정 개선: 환경별 자동 감지
    let port = window.location.port;
    if (!port) {
        port = window.location.protocol === 'https:' ? '443' : '8002';
    }
    
    return `${protocol}//${host}:${port}`;
}

function connectWebSocket() {
    // 이미 연결 중이면 중복 연결 방지
    if (wsConnectionState === 'connecting') {
        addDebugLog('WebSocket 연결이 이미 진행 중입니다', 'warning');
        return;
    }
    
    // 최대 재연결 시도 횟수 확인
    if (wsReconnectAttempts >= wsMaxReconnectAttempts) {
        addDebugLog(`최대 재연결 시도 횟수(${wsMaxReconnectAttempts})에 도달했습니다`, 'error');
        updateConnectionStatus('error', '연결 실패');
        return;
    }
    
    wsConnectionState = 'connecting';
    wsReconnectAttempts++;
    
    const clientId = 'enhanced-ui-' + Math.random().toString(36).substr(2, 9);
    const channels = 'analysis,alerts';
    
    // 🔧 개선: 경로 파라미터 방식으로 변경 (쿼리 파라미터 문제 해결)
    const baseUrl = getWebSocketURL();
    const wsUrl = `${baseUrl}/ws/${clientId}/${channels}`;
    
    addDebugLog(`WebSocket 연결 시도 #${wsReconnectAttempts}: ${wsUrl}`, 'info');
    updateConnectionStatus('connecting', '연결 중...');
    
    try {
        ws = new WebSocket(wsUrl);
        
        // 🔧 연결 타임아웃 설정 (10초)
        const connectionTimeout = setTimeout(() => {
            if (wsConnectionState === 'connecting') {
                addDebugLog('WebSocket 연결 타임아웃 (10초)', 'error');
                ws.close();
                scheduleReconnect();
            }
        }, 10000);
        
        ws.onopen = () => {
            clearTimeout(connectionTimeout);
            wsConnectionState = 'connected';
            wsReconnectAttempts = 0; // 성공 시 재연결 카운터 리셋
            wsReconnectDelay = 1000; // 재연결 지연시간 리셋
            
            addDebugLog('✅ WebSocket 연결 성공', 'success');
            updateConnectionStatus('connected', '연결됨');
            updateConnectionCount();
            
            // 🔧 하트비트 시작
            startHeartbeat();
            
            showNotification('실시간 시스템에 연결되었습니다', 'success');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                addDebugLog(`WebSocket 메시지 수신: ${data.type}`, 'info');
                handleWebSocketMessage(data);
            } catch (error) {
                addDebugLog(`메시지 파싱 오류: ${error.message}`, 'error');
            }
        };
        
        ws.onclose = (event) => {
            clearTimeout(connectionTimeout);
            wsConnectionState = 'disconnected';
            stopHeartbeat();
            
            addDebugLog(`WebSocket 연결 종료: 코드=${event.code}, 이유=${event.reason}`, 'warning');
            updateConnectionStatus('disconnected', '연결 끊김');
            
            // 🔧 정상 종료가 아닌 경우에만 재연결
            if (event.code !== 1000 && event.code !== 1001) {
                scheduleReconnect();
            }
        };
        
        ws.onerror = (error) => {
            clearTimeout(connectionTimeout);
            addDebugLog(`WebSocket 오류: ${error.type || error.message || '알 수 없는 오류'}`, 'error');
            updateConnectionStatus('error', '연결 오류');
            
            // 즉시 재연결 시도하지 않고 스케줄링
            scheduleReconnect();
        };
        
    } catch (error) {
        wsConnectionState = 'disconnected';
        addDebugLog(`WebSocket 생성 오류: ${error.message}`, 'error');
        updateConnectionStatus('error', '연결 실패');
        scheduleReconnect();
    }
}

// 🔧 지수 백오프를 적용한 재연결 스케줄링
function scheduleReconnect() {
    if (wsReconnectAttempts >= wsMaxReconnectAttempts) {
        addDebugLog('최대 재연결 시도 횟수에 도달하여 재연결을 중단합니다', 'error');
        updateConnectionStatus('error', '연결 포기');
        showNotification('서버 연결에 실패했습니다. 페이지를 새로고침해주세요.', 'error');
        return;
    }
    
    // 🔧 지수 백오프: 1초 → 2초 → 4초 → 8초 → ... (최대 30초)
    wsReconnectDelay = Math.min(wsReconnectDelay * 2, 30000);
    
    addDebugLog(`${wsReconnectDelay/1000}초 후 재연결 시도 예정...`, 'info');
    updateConnectionStatus('waiting', `${wsReconnectDelay/1000}초 후 재연결`);
    
    setTimeout(() => {
        if (wsConnectionState !== 'connected') {
            connectWebSocket();
        }
    }, wsReconnectDelay);
}

// 🔧 하트비트 (Ping/Pong) 메커니즘
function startHeartbeat() {
    stopHeartbeat(); // 기존 하트비트 정리
    
    wsHeartbeatInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            try {
                ws.send(JSON.stringify({
                    type: 'ping',
                    timestamp: Date.now()
                }));
                addDebugLog('하트비트 전송', 'info');
            } catch (error) {
                addDebugLog(`하트비트 전송 실패: ${error.message}`, 'error');
            }
        }
    }, 30000); // 30초마다 ping
}

function stopHeartbeat() {
    if (wsHeartbeatInterval) {
        clearInterval(wsHeartbeatInterval);
        wsHeartbeatInterval = null;
    }
}

// 🔧 연결 상태 시각화 개선
function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connectionStatus');
    const statusText = document.getElementById('connectionStatusText');
    
    if (!statusElement || !statusText) return;
    
    // 기존 상태 클래스 제거
    statusElement.className = 'connection-status';
    
    const statusConfig = {
        'connected': {
            class: 'connected',
            icon: 'fas fa-circle',
            color: '#4CAF50'
        },
        'connecting': {
            class: 'connecting',
            icon: 'fas fa-circle animate-pulse',
            color: '#FF9800'
        },
        'disconnected': {
            class: 'disconnected',
            icon: 'fas fa-circle',
            color: '#f44336'
        },
        'waiting': {
            class: 'waiting',
            icon: 'fas fa-clock',
            color: '#2196F3'
        },
        'error': {
            class: 'error',
            icon: 'fas fa-exclamation-circle',
            color: '#f44336'
        }
    };
    
    const config = statusConfig[status] || statusConfig['disconnected'];
    statusElement.classList.add(config.class);
    statusText.innerHTML = `
        <i class="${config.icon}" style="color: ${config.color}; margin-right: 5px;"></i>
        ${message}
    `;
}

function handleWebSocketMessage(data) {
    addDebugLog(`WebSocket 메시지: ${data.type}, job_id: ${data.job_id}`, 'info');
    
    // 🔧 하트비트 응답 처리
    if (data.type === 'pong') {
        addDebugLog('하트비트 응답 수신', 'info');
        return;
    }
    
    if (data.type === 'analysis_progress' && data.job_id === currentJobId) {
        updateProgress(data.progress, data.processed, data.total);
    } else if (data.type === 'analysis_completed' && data.job_id === currentJobId) {
        updateProgress(100, data.total_processed, data.total_processed);
        showNotification(`분석이 완료되었습니다! 평균 점수: ${data.average_score}점`, 'success');
        
        // 완료 알림과 다운로드 버튼 표시
        showCompletionActions(data.job_id, data.average_score);
        
        setTimeout(() => {
            loadRecentJobs();
            showResultsChart();
        }, 1000);
    } else if (data.type === 'analysis_failed' && data.job_id === currentJobId) {
        showNotification('분석 중 오류가 발생했습니다: ' + data.error, 'error');
        resetAnalysisButton();
    }
}

// 분석 완료 시 액션 버튼 표시
function showCompletionActions(jobId, avgScore) {
    const actionDiv = document.createElement('div');
    actionDiv.className = 'completion-actions animate__animated animate__fadeInUp';
    actionDiv.innerHTML = `
        <div style="background: white; border-radius: 12px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h4 style="color: var(--success-color); margin-bottom: 15px;">
                <i class="fas fa-check-circle"></i> 분석이 완료되었습니다!
            </h4>
            <p style="margin-bottom: 20px;">평균 점수: <strong style="font-size: 1.5rem; color: var(--primary-color);">${avgScore}점</strong></p>
            
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button class="button" onclick="viewResults('${jobId}')">
                    <i class="fas fa-chart-bar"></i> 결과 상세보기
                </button>
                <button class="button secondary" onclick="showDownloadOptions('${jobId}')">
                    <i class="fas fa-download"></i> 결과 다운로드
                </button>
            </div>
        </div>
    `;
    
    // 진행률 바 아래에 추가
    const progressContainer = document.querySelector('.progress-container');
    if (progressContainer && progressContainer.parentNode) {
        progressContainer.parentNode.insertBefore(actionDiv, progressContainer.nextSibling);
        
        // 30초 후 자동 제거
        setTimeout(() => {
            actionDiv.style.opacity = '0';
            setTimeout(() => actionDiv.remove(), 500);
        }, 30000);
    }
}

function updateConnectionCount() {
    fetch('/health')
    .then(response => response.json())
    .then(data => {
        const count = data.components?.connection_count || '0';
        const countElement = document.getElementById('connectionCount');
        if (countElement) {
            countElement.textContent = count;
        }
        addDebugLog(`연결 수 업데이트: ${count}`, 'info');
    })
    .catch(error => {
        const countElement = document.getElementById('connectionCount');
        if (countElement) {
            countElement.textContent = '?';
        }
        addDebugLog(`연결 수 업데이트 실패: ${error.message}`, 'error');
    });
}

// 📁 파일 업로드 시스템
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        addDebugLog(`드래그앤드롭 파일: ${files[0].name}`, 'info');
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        addDebugLog(`파일 선택: ${file.name}`, 'info');
        handleFile(file);
    }
}

function handleFile(file) {
    // 파일 크기 체크 (10MB 제한)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('파일 크기가 10MB를 초과합니다. 더 작은 파일을 선택해주세요.', 'error');
        return;
    }
    
    // 파일 형식 체크
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
        showNotification('지원하지 않는 파일 형식입니다. Excel 또는 CSV 파일을 선택해주세요.', 'error');
        return;
    }
    
    selectedFile = file;
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = false;
    
    addDebugLog(`파일 검증 완료: ${file.name} (${formatFileSize(file.size)})`, 'success');
    uploadFile(file);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    document.getElementById('fileStatus').textContent = '업로드 중...';
    addDebugLog('파일 업로드 시작', 'info');
    
    const uploadStartTime = Date.now();
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        addDebugLog(`업로드 응답 상태: ${response.status} ${response.statusText}`, 'info');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    })
    .then(data => {
        const uploadTime = Date.now() - uploadStartTime;
        addDebugLog(`업로드 완료 (${uploadTime}ms): 파일 ID = ${data.id}`, 'success');
        
        if (data.id) {
            selectedFile.fileId = data.id;
            document.getElementById('fileStatus').textContent = 
                `업로드 완료 (${data.total_records || '?'}건 데이터)`;
            showNotification('파일이 성공적으로 업로드되었습니다.', 'success');
            
            if (data.total_records) {
                addDebugLog(`데이터 분석: 총 ${data.total_records}건, AIRISS 준비=${data.airiss_ready}, 하이브리드 준비=${data.hybrid_ready}`, 'info');
            }
        } else {
            throw new Error(data.detail || '업로드 실패: 파일 ID를 받지 못했습니다');
        }
    })
    .catch(error => {
        addDebugLog(`업로드 오류: ${error.message}`, 'error');
        document.getElementById('fileStatus').textContent = '업로드 실패';
        showNotification('파일 업로드 중 오류: ' + error.message, 'error');
    });
}

// 🧠 분석 시작 시스템
function startAnalysis() {
    // 테스트를 위해 바로 분석 시작 (설정 모달 건너뛰기)
    if (!selectedFile || !selectedFile.fileId) {
        showNotification('먼저 파일을 업로드해주세요.', 'error');
        addDebugLog('파일이 업로드되지 않았습니다. selectedFile:', selectedFile);
        return;
    }
    
    const analysisData = {
        file_id: selectedFile.fileId,
        sample_size: 10,
        analysis_mode: 'hybrid',
        enable_ai_feedback: false,
        openai_model: 'gpt-3.5-turbo',
        max_tokens: 1200
    };
    
    addDebugLog(`분석 요청 데이터: ${JSON.stringify(analysisData, null, 2)}`, 'info');
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('loading');
    document.getElementById('progressText').textContent = '분석 시작 중...';
    
    const analysisStartTime = Date.now();
    
    const timeoutId = setTimeout(() => {
        addDebugLog('분석 요청 타임아웃 (30초)', 'error');
        showNotification('분석 시작 요청이 타임아웃되었습니다. 다시 시도해주세요.', 'error');
        resetAnalysisButton();
    }, 30000);
    
    fetch('/analysis/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(analysisData)
    })
    .then(response => {
        clearTimeout(timeoutId);
        const responseTime = Date.now() - analysisStartTime;
        addDebugLog(`분석 API 응답 시간: ${responseTime}ms, 상태: ${response.status}`, 'info');
        
        if (!response.ok) {
            return response.text().then(text => {
                addDebugLog(`분석 API 오류 응답: ${text}`, 'error');
                try {
                    const errorData = JSON.parse(text);
                    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
                } catch (jsonError) {
                    throw new Error(`HTTP ${response.status}: ${text}`);
                }
            });
        }
        
        return response.json();
    })
    .then(data => {
        addDebugLog(`분석 시작 성공: Job ID = ${data.job_id}`, 'success');
        
        if (data.job_id) {
            currentJobId = data.job_id;
            showNotification('AI 분석이 시작되었습니다. 실시간으로 진행상황을 확인할 수 있습니다.', 'success');
            updateProgress(0, 0, analysisData.sample_size);
            
            // 분석 상태 폴링 시작
            pollAnalysisStatus(data.job_id);
        } else {
            throw new Error(data.detail || '분석 시작 실패: Job ID를 받지 못했습니다');
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        addDebugLog(`분석 시작 오류: ${error.message}`, 'error');
        showNotification('분석 시작 중 오류: ' + error.message, 'error');
        resetAnalysisButton();
    });
}



// ============================================
// 분석 설정 관련 함수들 (AIRISS v4.0 개선)
// ============================================

// 분석 설정 모달 열기
function openAnalysisSettings() {
    if (!selectedFile || !selectedFile.fileId) {
        showNotification('먼저 파일을 업로드해주세요.', 'error');
        return;
    }
    
    document.getElementById('analysisSettingsModal').style.display = 'flex';
    updateEstimates();
    addDebugLog('분석 설정 모달 열림', 'info');
}

// 분석 설정 모달 닫기
function closeAnalysisSettings() {
    document.getElementById('analysisSettingsModal').style.display = 'none';
    addDebugLog('분석 설정 모달 닫힘', 'info');
}

// AI 설정 토글
function toggleAISettings() {
    const enableAI = document.getElementById('enableAI').checked;
    const aiSettings = document.getElementById('aiSettings');
    const costEstimate = document.getElementById('costEstimate');
    
    if (enableAI) {
        aiSettings.style.display = 'block';
        costEstimate.style.display = 'flex';
    } else {
        aiSettings.style.display = 'none';
        costEstimate.style.display = 'none';
    }
    
    updateEstimates();
}

// API Key 표시/숨기기
function toggleApiKeyVisibility() {
    const apiKeyInput = document.getElementById('apiKey');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        eyeIcon.className = 'fas fa-eye-slash';
    } else {
        apiKeyInput.type = 'password';
        eyeIcon.className = 'fas fa-eye';
    }
}

// API Key 검증
function validateApiKey() {
    const apiKey = document.getElementById('apiKey').value;
    
    if (apiKey && !apiKey.startsWith('sk-')) {
        showNotification('올바른 OpenAI API Key 형식이 아닙니다.', 'warning');
        return false;
    }
    
    if (apiKey && apiKey.length < 40) {
        showNotification('API Key가 너무 짧습니다.', 'warning');
        return false;
    }
    
    return true;
}

// 예상 시간 및 비용 업데이트
function updateEstimates() {
    const sampleSizeElement = document.querySelector('input[name="sampleSize"]:checked');
    const sampleSize = sampleSizeElement ? sampleSizeElement.value : '10';
    const enableAI = document.getElementById('enableAI').checked;
    const aiModel = document.getElementById('aiModel').value;
    
    let actualSize = sampleSize === 'all' ? 
        (selectedFile?.totalRecords || 100) : parseInt(sampleSize);
    
    // 예상 시간 계산
    let timePerRecord = enableAI ? 0.5 : 0.1; // AI 사용시 더 오래 걸림
    let estimatedSeconds = actualSize * timePerRecord;
    let timeText = estimatedSeconds < 60 ? 
        `약 ${Math.ceil(estimatedSeconds)}초` : 
        `약 ${Math.ceil(estimatedSeconds / 60)}분`;
    
    document.getElementById('estimatedTime').textContent = timeText;
    
    // 예상 비용 계산 (AI 사용시만)
    if (enableAI) {
        let costPerRecord = 0;
        switch(aiModel) {
            case 'gpt-3.5-turbo':
                costPerRecord = 0.002; // $0.002 per record
                break;
            case 'gpt-4':
                costPerRecord = 0.02; // $0.02 per record
                break;
            case 'gpt-4-turbo':
                costPerRecord = 0.01; // $0.01 per record
                break;
        }
        
        let estimatedCost = actualSize * costPerRecord;
        document.getElementById('estimatedCost').textContent = 
            `$${estimatedCost.toFixed(2)} (약 ${Math.ceil(estimatedCost * 1300)}원)`;
    }
}

// 설정에 따라 분석 시작
function startAnalysisWithSettings() {
    addDebugLog('=== 설정 기반 AI 분석 시작 ===', 'info');
    
    // 설정값 수집
    const sampleSizeElement = document.querySelector('input[name="sampleSize"]:checked');
    const sampleSize = sampleSizeElement ? sampleSizeElement.value : '10';
    const enableAI = document.getElementById('enableAI').checked;
    const aiModel = document.getElementById('aiModel').value;
    const apiKey = document.getElementById('apiKey').value;
    const maxTokens = parseInt(document.getElementById('maxTokens').value) || 1200;
    const analysisMode = document.getElementById('analysisMode').value;
    
    // AI 사용시 API Key 검증
    if (enableAI && !apiKey) {
        showNotification('AI 분석을 사용하려면 OpenAI API Key를 입력해주세요.', 'error');
        return;
    }
    
    if (enableAI && !validateApiKey()) {
        return;
    }
    
    // 실제 분석 인원수 계산
    let actualSampleSize = sampleSize === 'all' ? 
        (selectedFile?.totalRecords || 9999) : parseInt(sampleSize);
    
    // 분석 요청 데이터 구성
    const analysisData = {
        file_id: selectedFile.fileId,
        sample_size: actualSampleSize,
        analysis_mode: analysisMode,
        enable_ai_feedback: enableAI,
        openai_api_key: enableAI ? apiKey : null,
        openai_model: enableAI ? aiModel : 'gpt-3.5-turbo',
        max_tokens: maxTokens
    };
    
    addDebugLog(`분석 설정: ${JSON.stringify({
        ...analysisData,
        openai_api_key: analysisData.openai_api_key ? '***' : null
    }, null, 2)}`, 'info');
    
    // 모달 닫기
    closeAnalysisSettings();
    
    // 분석 시작
    const startAnalysisBtn = document.getElementById('startAnalysisBtn');
    startAnalysisBtn.disabled = true;
    startAnalysisBtn.classList.add('loading');
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('loading');
    document.getElementById('progressText').textContent = '분석 시작 중...';
    
    fetch('/analysis/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(analysisData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        addDebugLog(`분석 시작 성공: Job ID = ${data.job_id}`, 'success');
        
        if (data.job_id) {
            currentJobId = data.job_id;
            showNotification(
                `AI 분석이 시작되었습니다. ${actualSampleSize}명 분석 중...`, 
                'success'
            );
            updateProgress(0, 0, actualSampleSize);
            
            // 완료시 자동으로 결과 다운로드 버튼 표시
            window.currentAnalysisSettings = analysisData;
        }
    })
    .catch(error => {
        addDebugLog(`분석 시작 오류: ${error.message || error.detail}`, 'error');
        showNotification('분석 시작 중 오류: ' + (error.detail || error.message), 'error');
        resetAnalysisButton();
        startAnalysisBtn.disabled = false;
        startAnalysisBtn.classList.remove('loading');
    });
}

function resetAnalysisButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('loading');
    document.getElementById('progressText').textContent = '대기 중';
}

function updateProgress(percent, processed, total) {
    document.getElementById('progressFill').style.width = percent + '%';
    document.getElementById('progressText').textContent = 
        `진행률: ${percent.toFixed(1)}% (${processed}/${total})`;
    
    addDebugLog(`진행률 업데이트: ${percent.toFixed(1)}% (${processed}/${total})`, 'info');
}

// 📊 향상된 차트 시각화 시스템
function showResultsChart() {
    const chartContainer = document.getElementById('chartContainer');
    chartContainer.classList.remove('hidden');
    
    if (resultsChart) {
        resultsChart.destroy();
    }
    
    // 실제 분석 데이터가 있으면 사용, 없으면 샘플 데이터
    const analysisData = window.lastAnalysisResult || sampleAnalysisResults;
    
    const ctx = document.getElementById('resultsChart').getContext('2d');
    
    // 그라데이션 배경 생성
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(255, 87, 34, 0.4)');
    gradient.addColorStop(1, 'rgba(248, 156, 38, 0.1)');
    
    resultsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: analysisData.labels,
            datasets: [{
                label: '현재 역량',
                data: analysisData.datasets[0].data,
                backgroundColor: gradient,
                borderColor: 'rgba(255, 87, 34, 1)',
                borderWidth: 3,
                pointBackgroundColor: 'rgba(255, 87, 34, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 8,
                pointHoverRadius: 10
            }, {
                label: '목표 수준',
                data: [85, 85, 85, 85, 85, 85, 85, 85], // 목표선
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                borderColor: 'rgba(76, 175, 80, 0.5)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        font: {
                            size: 11
                        }
                    },
                    grid: {
                        color: 'rgba(255, 87, 34, 0.1)',
                        circular: true
                    },
                    pointLabels: {
                        font: {
                            size: 13,
                            weight: 'bold'
                        },
                        color: '#333',
                        padding: 15
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333',
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 87, 34, 0.95)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    cornerRadius: 8,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.r;
                            let emoji = '';
                            
                            if (value >= 90) emoji = '🏆';
                            else if (value >= 80) emoji = '⭐';
                            else if (value >= 70) emoji = '👍';
                            else emoji = '📈';
                            
                            return `${emoji} ${label}: ${value}점`;
                        },
                        afterLabel: function(context) {
                            const dimensionName = context.label;
                            const recommendations = {
                                '업무성과': '주간 성과 리뷰를 통해 진척도 관리',
                                'KPI달성': '핵심 지표에 집중하여 효율성 제고',
                                '태도': '긍정적 피드백 문화 조성',
                                '커뮤니케이션': '적극적 경청 스킬 개발',
                                '리더십': '팀 빌딩 활동 참여',
                                '협업': '크로스팀 프로젝트 참여',
                                '전문성': '관련 분야 교육 수강',
                                '창의혁신': '아이디어 브레인스토밍 참여'
                            };
                            
                            if (context.parsed.r < 70) {
                                return `💡 개선 제안: ${recommendations[dimensionName] || '지속적 역량 개발'}`;
                            }
                            return '';
                        }
                    }
                }
            },
            elements: {
                line: {
                    borderWidth: 3,
                    tension: 0.1
                },
                point: {
                    radius: 6,
                    hoverRadius: 10,
                    hoverBorderWidth: 3
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    addDebugLog('향상된 분석 결과 차트 표시 완료', 'success');
    
    // 결과 카드 생성
    createEnhancedResultCards(analysisData);
}

// 향상된 결과 카드 생성
function createEnhancedResultCards(analysisData) {
    const resultsGrid = document.getElementById('resultsGrid');
    const labels = analysisData.labels;
    const data = analysisData.datasets[0].data;
    
    // 전체 평균 계산
    const average = data.reduce((a, b) => a + b, 0) / data.length;
    const grade = getGrade(average);
    
    let cardsHTML = `
        <!-- 종합 점수 카드 -->
        <div class="result-card animate__animated animate__fadeInUp" style="grid-column: span 2; background: linear-gradient(135deg, #FF5722, #F89C26); color: white;">
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 10px;">${grade.badge}</div>
                <div style="font-size: 2.5rem; font-weight: bold;">${grade.grade} 등급</div>
                <div style="font-size: 1.2rem; margin-top: 10px;">${grade.description}</div>
                <div style="font-size: 3rem; margin-top: 20px;">${average.toFixed(1)}점</div>
                <div style="font-size: 1rem; opacity: 0.9;">종합 점수</div>
            </div>
        </div>
    `;
    
    // 개별 영역 카드
    labels.forEach((label, index) => {
        const score = data[index];
        const diff = score - average;
        const trend = diff > 5 ? '↑' : diff < -5 ? '↓' : '→';
        const trendColor = diff > 5 ? '#4CAF50' : diff < -5 ? '#f44336' : '#FF9800';
        const strength = score >= 85;
        
        cardsHTML += `
            <div class="result-card animate__animated animate__fadeInUp" style="animation-delay: ${index * 0.1 + 0.2}s;">
                ${strength ? '<div class="strength-badge">강점</div>' : ''}
                <div class="result-score" style="color: ${getScoreColor(score)}">${score}</div>
                <div class="result-label">${label}</div>
                <div style="text-align: center; margin-top: 10px;">
                    <span style="color: ${trendColor}; font-size: 1.2rem;">${trend}</span>
                    <span style="font-size: 0.9rem; color: #666; margin-left: 5px;">평균 대비 ${diff > 0 ? '+' : ''}${diff.toFixed(1)}</span>
                </div>
                ${score < 70 ? `<div class="improvement-hint">💡 개선 필요</div>` : ''}
            </div>
        `;
    });
    
    // 인사이트 카드 추가
    cardsHTML += `
        <div class="result-card animate__animated animate__fadeInUp" style="animation-delay: 0.8s; grid-column: span 2; background: #f8f9fa;">
            <h4 style="color: var(--primary-color); margin-bottom: 15px;"><i class="fas fa-lightbulb"></i> AI 분석 인사이트</h4>
            <div class="insight-content">
                ${generateInsights(labels, data, average)}
            </div>
        </div>
    `;
    
    resultsGrid.innerHTML = cardsHTML;
    resultsGrid.style.display = 'grid';
    
    addDebugLog('향상된 결과 카드 생성 완료', 'success');
}

// 등급 판정 함수
function getGrade(score) {
    if (score >= 95) return { grade: 'S', description: '탁월함 (TOP 1%)', badge: '🏆' };
    if (score >= 90) return { grade: 'A+', description: '매우 우수 (TOP 5%)', badge: '⭐⭐⭐' };
    if (score >= 85) return { grade: 'A', description: '우수 (TOP 10%)', badge: '⭐⭐' };
    if (score >= 80) return { grade: 'B+', description: '양호 (TOP 20%)', badge: '⭐' };
    if (score >= 75) return { grade: 'B', description: '평균 이상 (TOP 30%)', badge: '✨' };
    if (score >= 70) return { grade: 'C+', description: '평균 (TOP 40%)', badge: '👍' };
    if (score >= 60) return { grade: 'C', description: '개선 필요 (TOP 60%)', badge: '📈' };
    return { grade: 'D', description: '집중 관리 필요', badge: '🚨' };
}

// 점수별 색상
function getScoreColor(score) {
    if (score >= 90) return '#4CAF50';
    if (score >= 80) return '#8BC34A';
    if (score >= 70) return '#FF9800';
    if (score >= 60) return '#FF5722';
    return '#f44336';
}

// AI 인사이트 생성
function generateInsights(labels, scores, average) {
    const strengths = [];
    const improvements = [];
    
    labels.forEach((label, index) => {
        if (scores[index] >= 85) {
            strengths.push({ label, score: scores[index] });
        } else if (scores[index] < 70) {
            improvements.push({ label, score: scores[index] });
        }
    });
    
    let insights = '<div class="insights-grid">';
    
    // 강점 분석
    if (strengths.length > 0) {
        insights += '<div class="insight-section">';
        insights += '<h5 style="color: #4CAF50;"><i class="fas fa-star"></i> 핵심 강점</h5>';
        insights += '<ul style="margin: 10px 0;">';
        strengths.slice(0, 3).forEach(s => {
            insights += `<li><strong>${s.label}</strong> - ${s.score}점 (탁월함)</li>`;
        });
        insights += '</ul>';
        insights += '</div>';
    }
    
    // 개선 영역
    if (improvements.length > 0) {
        insights += '<div class="insight-section">';
        insights += '<h5 style="color: #FF5722;"><i class="fas fa-chart-line"></i> 우선 개선 영역</h5>';
        insights += '<ul style="margin: 10px 0;">';
        improvements.slice(0, 3).forEach(i => {
            const recommendation = getRecommendation(i.label);
            insights += `<li><strong>${i.label}</strong> - ${i.score}점<br><span style="font-size: 0.9rem; color: #666;">→ ${recommendation}</span></li>`;
        });
        insights += '</ul>';
        insights += '</div>';
    }
    
    // 성과 예측
    insights += '<div class="insight-section" style="grid-column: span 2;">';
    insights += '<h5 style="color: #FF5722;"><i class="fas fa-chart-line"></i> 성과 예측</h5>';
    
    const prediction = predictPerformance(average);
    insights += `
        <div class="prediction-grid">
            <div class="prediction-item">
                <i class="fas fa-trending-${prediction.trend}" style="color: ${prediction.color};"></i>
                <strong>6개월 후 예상 트렌드:</strong> ${prediction.text}
            </div>
            <div class="prediction-item">
                <i class="fas fa-percentage" style="color: #FF9800;"></i>
                <strong>성공 확률:</strong> ${prediction.probability}%
            </div>
            <div class="prediction-item">
                <i class="fas fa-user-check" style="color: #4CAF50;"></i>
                <strong>승진 준비도:</strong> ${prediction.readiness}
            </div>
            <div class="prediction-item">
                <i class="fas fa-door-open" style="color: #f44336;"></i>
                <strong>이직 위험도:</strong> ${prediction.turnover}
            </div>
        </div>
    `;
    
    insights += '</div>';
    insights += '</div>';
    
    return insights;
}

// 영역별 개선 권고사항
function getRecommendation(dimension) {
    const recommendations = {
        '업무성과': '주간 목표 설정 및 리뷰 프로세스 도입',
        'KPI달성': '핵심 지표 대시보드 활용 및 일일 모니터링',
        '태도': '멘토링 프로그램 참여 및 긍정 심리 교육',
        '커뮤니케이션': '프레젠테이션 스킬 워크샵 수강',
        '리더십': '리더십 코칭 프로그램 참여',
        '협업': '크로스 펑셔널 프로젝트 적극 참여',
        '전문성': 'LinkedIn Learning 또는 Coursera 강의 수강',
        '창의혁신': '디자인 씽킹 워크샵 참여'
    };
    return recommendations[dimension] || '지속적인 자기계발 필요';
}

// 성과 예측 함수
function predictPerformance(avgScore) {
    if (avgScore >= 85) {
        return {
            trend: 'up',
            color: '#4CAF50',
            text: '지속 상승',
            probability: 85,
            readiness: '높음',
            turnover: '낮음 (10%)'
        };
    } else if (avgScore >= 70) {
        return {
            trend: 'right',
            color: '#FF9800',
            text: '안정적 유지',
            probability: 70,
            readiness: '보통',
            turnover: '보통 (25%)'
        };
    } else {
        return {
            trend: 'down',
            color: '#f44336',
            text: '주의 필요',
            probability: 50,
            readiness: '낮음',
            turnover: '높음 (40%)'
        };
    }
}

// 📋 작업 관리 시스템
function loadRecentJobs() {
    addDebugLog('최근 작업 목록 조회 시작', 'info');
    
    fetch('/analysis/jobs')
    .then(response => {
        addDebugLog(`작업 목록 응답: ${response.status}`, 'info');
        return response.json();
    })
    .then(jobs => {
        addDebugLog(`작업 수: ${jobs.length}`, 'info');
        displayJobs(jobs);
    })
    .catch(error => {
        addDebugLog(`작업 목록 조회 오류: ${error.message}`, 'error');
        document.getElementById('recentJobs').innerHTML = 
            '<p style="color: var(--danger-color); text-align: center;"><i class="fas fa-exclamation-triangle"></i> 작업 목록을 불러올 수 없습니다.</p>';
    });
}

function displayJobs(jobs) {
    const container = document.getElementById('recentJobs');
    
    if (jobs.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 15px; color: #ccc;"></i>
                <p>최근 분석 작업이 없습니다.</p>
                <p style="font-size: 0.9rem; margin-top: 10px;">파일을 업로드하여 첫 번째 분석을 시작해보세요!</p>
            </div>
        `;
        return;
    }
    
    let html = '<h3 style="margin-bottom: 20px; color: var(--primary-color);"><i class="fas fa-history"></i> 최근 분석 작업</h3>';
    
    jobs.forEach((job, index) => {
        const createdDate = new Date(job.created_at || Date.now()).toLocaleString();
        const statusIcon = job.status === 'completed' ? 'fas fa-check-circle' : 
                         job.status === 'failed' ? 'fas fa-times-circle' : 'fas fa-clock';
        const statusColor = job.status === 'completed' ? 'var(--success-color)' : 
                          job.status === 'failed' ? 'var(--danger-color)' : 'var(--warning-color)';
        
        html += `
            <div class="job-item animate__animated animate__fadeInUp" style="animation-delay: ${index * 0.1}s;">
                <div class="job-info">
                    <div class="job-title">
                        <i class="fas fa-file-excel" style="color: var(--primary-color); margin-right: 8px;"></i>
                        ${job.filename || 'Unknown File'}
                    </div>
                    <div class="job-meta">
                        <i class="${statusIcon}" style="color: ${statusColor}; margin-right: 5px;"></i>
                        ${job.processed || 0}명 분석 완료 • ${createdDate}
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button class="button" onclick="viewResults('${job.job_id}')" 
                            style="padding: 8px 16px; font-size: 0.9rem;"
                            ${job.status !== 'completed' ? 'disabled' : ''}>
                        <i class="fas fa-chart-bar"></i> 결과 보기
                    </button>
                    ${job.status === 'completed' ? `
                        <button class="button secondary" onclick="showDownloadOptions('${job.job_id}')" 
                                style="padding: 8px 16px; font-size: 0.9rem;">
                            <i class="fas fa-download"></i> 다운로드
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// 🔄 분석 상태 폴링
async function pollAnalysisStatus(jobId) {
    addDebugLog(`분석 상태 폴링 시작: ${jobId}`, 'info');
    const maxAttempts = 300; // 최대 5분 (1초 간격)
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        try {
            const statusUrl = `/analysis/status/${jobId}`;
            addDebugLog(`상태 확인 요청 #${attempts + 1}: ${statusUrl}`, 'info');
            
            const response = await fetch(statusUrl);
            
            if (!response.ok) {
                const errorData = await response.json();
                addDebugLog(`상태 확인 에러: ${JSON.stringify(errorData)}`, 'error');
                throw new Error('상태 확인 실패');
            }
            
            const status = await response.json();
            addDebugLog(`상태 데이터: ${JSON.stringify(status)}`, 'info');
            
            // 진행률 업데이트
            updateProgress(status.progress || 0, status.processed || 0, status.total || 0);
            
            if (status.status === 'completed') {
                addDebugLog('분석 완료!', 'success');
                showNotification('✅ 분석이 완료되었습니다!', 'success');
                resetAnalysisButton();
                loadRecentJobs();
                
                // 결과 표시
                if (status.average_score) {
                    showCompletionActions(jobId, status.average_score);
                }
                return;
            } else if (status.status === 'failed') {
                addDebugLog(`분석 실패: ${status.error}`, 'error');
                throw new Error(status.error || '분석 실패');
            }
            
            // 1초 대기 후 다시 확인
            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
            
        } catch (error) {
            addDebugLog(`상태 확인 오류: ${error.message}`, 'error');
            showNotification(`분석 오류: ${error.message}`, 'error');
            resetAnalysisButton();
            return;
        }
    }
    
    addDebugLog('분석 시간 초과', 'error');
    showNotification('분석 시간이 초과되었습니다.', 'warning');
    resetAnalysisButton();
}

function viewResults(jobId) {
    addDebugLog(`결과 조회: ${jobId}`, 'info');
    
    // 결과 조회
    fetch(`/analysis/results/${jobId}`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                // 결과 데이터 저장
                window.lastAnalysisResult = processResultsForChart(data.results);
                
                // 차트 표시
                showResultsChart();
                
                // 다운로드 옵션 표시
                showDownloadOptions(jobId);
            } else {
                showNotification('분석 결과가 없습니다.', 'warning');
            }
        })
        .catch(error => {
            addDebugLog(`결과 조회 오류: ${error.message}`, 'error');
            showNotification('결과 조회 중 오류가 발생했습니다.', 'error');
        });
}



// ============================================
// 결과 다운로드 관련 함수들 (AIRISS v4.0 개선)
// ============================================

// 분석 결과 다운로드
function downloadResults(jobId, format = 'excel') {
    addDebugLog(`결과 다운로드 시작: ${jobId} (${format})`, 'info');
    
    const downloadBtn = event.target;
    const originalText = downloadBtn.innerHTML;
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 다운로드 중...';
    
    fetch(`/analysis/download/${jobId}/${format}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`다운로드 실패: ${response.statusText}`);
            }
            
            // 파일명 추출
            const contentDisposition = response.headers.get('content-disposition');
            let filename = `AIRISS_분석결과_${jobId}.${format === 'excel' ? 'xlsx' : format}`;
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            return response.blob().then(blob => ({ blob, filename }));
        })
        .then(({ blob, filename }) => {
            // 다운로드 실행
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            addDebugLog(`다운로드 완료: ${filename}`, 'success');
            showNotification(`분석 결과가 다운로드되었습니다: ${filename}`, 'success');
        })
        .catch(error => {
            addDebugLog(`다운로드 오류: ${error.message}`, 'error');
            showNotification(`다운로드 실패: ${error.message}`, 'error');
        })
        .finally(() => {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = originalText;
        });
}

// 다운로드 형식 선택 모달
function showDownloadOptions(jobId) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h3><i class="fas fa-download"></i> 결과 다운로드</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div class="modal-body">
                <p style="margin-bottom: 20px;">분석 결과를 다운로드할 형식을 선택하세요.</p>
                
                <div class="download-options">
                    <button class="download-option" onclick="downloadResults('${jobId}', 'excel'); this.closest('.modal-overlay').remove();">
                        <i class="fas fa-file-excel" style="font-size: 2rem; color: #1D6F42; margin-bottom: 10px;"></i>
                        <div><strong>Excel 파일</strong></div>
                        <div style="font-size: 0.85rem; color: #666;">요약 + 상세결과 (권장)</div>
                    </button>
                    
                    <button class="download-option" onclick="downloadResults('${jobId}', 'csv'); this.closest('.modal-overlay').remove();">
                        <i class="fas fa-file-csv" style="font-size: 2rem; color: #FF9800; margin-bottom: 10px;"></i>
                        <div><strong>CSV 파일</strong></div>
                        <div style="font-size: 0.85rem; color: #666;">단순 데이터</div>
                    </button>
                    
                    <button class="download-option" onclick="downloadResults('${jobId}', 'json'); this.closest('.modal-overlay').remove();">
                        <i class="fas fa-file-code" style="font-size: 2rem; color: #2196F3; margin-bottom: 10px;"></i>
                        <div><strong>JSON 파일</strong></div>
                        <div style="font-size: 0.85rem; color: #666;">개발자용</div>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // CSS 추가
    if (!document.getElementById('downloadOptionsStyle')) {
        const style = document.createElement('style');
        style.id = 'downloadOptionsStyle';
        style.textContent = `
            .download-options {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 20px;
            }
            
            .download-option {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 20px 15px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            
            .download-option:hover {
                border-color: var(--primary-color);
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            @media (max-width: 480px) {
                .download-options {
                    grid-template-columns: 1fr;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// 결과 데이터를 차트용으로 변환
function processResultsForChart(results) {
    // 8대 영역별 평균 점수 계산
    const dimensions = [
        '업무성과', 'KPI달성', '태도마인드셋', '커뮤니케이션역량', 
        '리더십협업역량', '지식전문성', '라이프스타일건강', '윤리사외행동'
    ];
    
    const scores = dimensions.map(dim => {
        const dimResults = results.filter(r => r[`${dim}_점수`]);
        if (dimResults.length > 0) {
            const sum = dimResults.reduce((acc, r) => acc + (r[`${dim}_점수`] || 0), 0);
            return Math.round(sum / dimResults.length);
        }
        return 75; // 기본값
    });
    
    return {
        labels: dimensions,
        datasets: [{
            label: '평균 점수',
            data: scores,
            backgroundColor: 'rgba(255, 87, 34, 0.2)',
            borderColor: 'rgba(255, 87, 34, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(255, 87, 34, 1)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6
        }]
    };
}

// 🛠️ 시스템 테스트
function testAnalysisAPI() {
    addDebugLog('=== 시스템 종합 테스트 시작 ===', 'info');
    const testBtn = document.getElementById('testApiBtn');
    testBtn.disabled = true;
    testBtn.textContent = '테스트 중...';
    
    let testResults = [];
    
    // 1. Health Check
    fetch('/health')
    .then(response => response.json())
    .then(data => {
        testResults.push({ name: 'Health Check', status: 'success', details: data.status });
        addDebugLog(`✅ Health Check: ${data.status}`, 'success');
        return fetch('/health/analysis');
    })
    .then(response => response.json())
    .then(data => {
        testResults.push({ name: 'Analysis Engine', status: data.status === 'healthy' ? 'success' : 'error', details: data.status });
        addDebugLog(`✅ Analysis Engine: ${data.status}`, data.status === 'healthy' ? 'success' : 'error');
        return fetch('/health/db');
    })
    .then(response => response.json())
    .then(data => {
        testResults.push({ name: 'Database', status: data.status === 'healthy' ? 'success' : 'error', details: `${data.files} files` });
        addDebugLog(`✅ Database: ${data.status}, 파일 수: ${data.files}`, data.status === 'healthy' ? 'success' : 'error');
        
        // 테스트 결과 요약
        const successCount = testResults.filter(r => r.status === 'success').length;
        const totalCount = testResults.length;
        
        if (successCount === totalCount) {
            showNotification(`시스템 테스트 완료! 모든 컴포넌트(${totalCount})가 정상 작동 중입니다.`, 'success');
        } else {
            showNotification(`시스템 테스트 완료. ${successCount}/${totalCount} 컴포넌트가 정상입니다.`, 'warning');
        }
        
        addDebugLog('=== 시스템 테스트 완료 ===', 'success');
    })
    .catch(error => {
        addDebugLog(`시스템 테스트 실패: ${error.message}`, 'error');
        showNotification('시스템 테스트 중 오류 발생: ' + error.message, 'error');
    })
    .finally(() => {
        testBtn.disabled = false;
        testBtn.innerHTML = '<i class="fas fa-tools"></i> 시스템 테스트';
    });
}

// 📥 샘플 데이터 다운로드
function showSampleData() {
    addDebugLog('샘플 데이터 생성 및 다운로드', 'info');
    
    const sampleData = `UID,이름,의견,성과등급,KPI점수
EMP001,김철수,매우 열심히 업무에 임하고 동료들과 원활한 소통을 하고 있습니다. 프로젝트 관리 능력이 뛰어나며 팀에 긍정적인 영향을 줍니다. 창의적인 아이디어로 업무 효율을 개선하고 있습니다.,A,85
EMP002,이영희,창의적인 아이디어로 프로젝트를 성공적으로 이끌었습니다. 고객과의 소통이 원활하고 문제 해결 능력이 우수합니다. 전문성 향상을 위해 지속적으로 학습하고 있습니다.,B+,78
EMP003,박민수,시간 관리와 업무 효율성 측면에서 개선이 필요합니다. 하지만 성실한 태도로 꾸준히 발전하고 있습니다. 팀워크는 양호한 편입니다.,C,65
EMP004,최영수,고객과의 소통이 뛰어나고 문제 해결 능력이 우수합니다. 동료들에게 도움을 주는 협업 정신이 훌륭합니다. 리더십 역량도 점차 성장하고 있습니다.,A,92
EMP005,한지민,팀워크가 좋고 협업 능력이 뛰어난 직원입니다. 새로운 기술 습득에 적극적이며 전문성을 지속적으로 향상시키고 있습니다. 혁신적인 사고로 업무 개선에 기여합니다.,B+,80`;
    
    const blob = new Blob([sampleData], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'AIRISS_샘플데이터.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showNotification('AIRISS 샘플 데이터가 다운로드되었습니다. 이 파일을 업로드하여 테스트해보세요!', 'success');
    addDebugLog('샘플 데이터 다운로드 완료', 'success');
}

// 🔧 수동 WebSocket 재연결 (사용자 요청 시)
function forceReconnectWebSocket() {
    addDebugLog('수동 WebSocket 재연결 시작', 'info');
    
    // 기존 연결 정리
    if (ws) {
        ws.close();
        ws = null;
    }
    
    // 재연결 카운터 리셋
    wsReconnectAttempts = 0;
    wsReconnectDelay = 1000;
    wsConnectionState = 'disconnected';
    
    // 즉시 재연결
    connectWebSocket();
    
    showNotification('WebSocket 재연결을 시도합니다...', 'info');
}

// 🚀 페이지 초기화
document.addEventListener('DOMContentLoaded', function() {
    addDebugLog('AIRISS v4.1 Enhanced UI 초기화 시작 (WebSocket 안정성 개선 버전)', 'info');
    
    // 🔧 연결 상태 UI 요소 추가 (없는 경우)
    if (!document.getElementById('connectionStatus')) {
        const statusContainer = document.createElement('div');
        statusContainer.id = 'connectionStatusContainer';
        statusContainer.innerHTML = `
            <div id="connectionStatus" class="connection-status disconnected">
                <span id="connectionStatusText">
                    <i class="fas fa-circle" style="color: #f44336; margin-right: 5px;"></i>
                    연결 준비 중...
                </span>
                <button onclick="forceReconnectWebSocket()" style="margin-left: 10px; padding: 2px 8px; font-size: 0.8rem;">
                    재연결
                </button>
            </div>
        `;
        document.body.insertBefore(statusContainer, document.body.firstChild);
    }
    
    // WebSocket 연결 (개선된 버전)
    connectWebSocket();
    
    // 연결 상태 업데이트
    updateConnectionCount();
    
    // 최근 작업 로드
    loadRecentJobs();
    
    // 정기 업데이트 (30초마다)
    setInterval(() => {
        updateConnectionCount();
        
        // 🔧 연결이 끊어진 상태에서 자동 재연결 시도
        if (wsConnectionState === 'disconnected' && wsReconnectAttempts < wsMaxReconnectAttempts) {
            addDebugLog('자동 재연결 조건 충족, 재연결 시도', 'info');
            connectWebSocket();
        }
    }, 30000);
    
    // 온보딩 체크 (첫 방문자용)
    const hasVisited = localStorage.getItem('airiss_visited');
    if (!hasVisited) {
        setTimeout(() => {
            showOnboarding();
            localStorage.setItem('airiss_visited', 'true');
        }, 2000);
    }
    
    addDebugLog('초기화 완료 - AIRISS v4.1 Enhanced 시스템 준비됨 (WebSocket 안정성 강화)', 'success');
    showNotification('AIRISS v4.1 Enhanced가 시작되었습니다! 파일을 업로드하여 AI 분석을 시작해보세요.', 'info');
});

// 페이지 언로드 시 WebSocket 정리
window.addEventListener('beforeunload', function() {
    if (ws) {
        ws.close();
        addDebugLog('WebSocket 연결 정리 완료', 'info');
    }
    stopHeartbeat();
});

// 키보드 단축키
document.addEventListener('keydown', function(e) {
    // Ctrl + U: 파일 업로드
    if (e.ctrlKey && e.key === 'u') {
        e.preventDefault();
        document.getElementById('fileInput').click();
    }
    
    // Ctrl + D: 디버그 토글
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        toggleDebugInfo();
    }
    
    // Ctrl + R: WebSocket 재연결 (Ctrl+R이 새로고침과 충돌하므로 Ctrl+Shift+R로 변경)
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
        e.preventDefault();
        forceReconnectWebSocket();
    }
    
    // F1: 도움말
    if (e.key === 'F1') {
        e.preventDefault();
        showOnboarding();
    }
});

// 🔧 CSS 스타일 추가 (연결 상태 UI용)
if (!document.getElementById('connectionStatusStyle')) {
    const style = document.createElement('style');
    style.id = 'connectionStatusStyle';
    style.textContent = `
        #connectionStatusContainer {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
            font-size: 0.9rem;
        }
        
        .connection-status {
            background: white;
            border-radius: 8px;
            padding: 8px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #f44336;
            transition: all 0.3s ease;
        }
        
        .connection-status.connected {
            border-left-color: #4CAF50;
        }
        
        .connection-status.connecting {
            border-left-color: #FF9800;
        }
        
        .connection-status.waiting {
            border-left-color: #2196F3;
        }
        
        .connection-status.error {
            border-left-color: #f44336;
        }
        
        .animate-pulse {
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
}
