// app/static/js/main.js
// AIRISS v4.0 Optimized 메인 JavaScript

class AIRISSApp {
    constructor() {
        this.selectedFile = null;
        this.currentJobId = null;
        this.ws = null;
        this.debugMode = false;
        this.resultsChart = null;
        this.isOnline = navigator.onLine;
        
        // 설정
        this.config = {
            wsHost: window.location.hostname,
            wsPort: window.location.port || (window.location.protocol === 'https:' ? 443 : 80),
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedFileTypes: ['.xlsx', '.xls', '.csv'],
            reconnectInterval: 3000,
            notificationTimeout: 5000
        };
        
        this.init();
    }
    
    // 🚀 초기화
    init() {
        this.addDebugLog('AIRISS v4.0 Optimized 초기화 시작', 'info');
        
        // DOM 로드 대기
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDOMContentLoaded());
        } else {
            this.onDOMContentLoaded();
        }
    }
    
    onDOMContentLoaded() {
        this.setupEventListeners();
        this.initializeWebSocket();
        this.updateConnectionCount();
        
        // 정기 업데이트
        setInterval(() => this.updateConnectionCount(), 30000);
        
        this.addDebugLog('초기화 완료 - AIRISS v4.0 시스템 준비됨', 'success');
        this.showNotification('AIRISS v4.0이 시작되었습니다!', 'info');
    }
    
    // 🎯 이벤트 리스너 설정
    setupEventListeners() {
        // 파일 입력
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // 드래그 앤 드롭
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('click', () => this.triggerFileSelect());
            uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
            uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        }
        
        // 키보드 단축키
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
        
        // 온라인/오프라인 이벤트
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));
        
        // 페이지 언로드 시 정리
        window.addEventListener('beforeunload', () => this.cleanup());
    }
    
    // 🌐 WebSocket 연결
    initializeWebSocket() {
        const clientId = 'optimized-ui-' + Math.random().toString(36).substr(2, 9);
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${this.config.wsHost}:${this.config.wsPort}/ws/${clientId}?channels=analysis,alerts`;
        
        this.addDebugLog(`WebSocket 연결 시도: ${wsUrl}`, 'info');
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.addDebugLog('WebSocket 연결 성공', 'success');
            this.updateConnectionStatus(true);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.addDebugLog(`WebSocket 메시지 수신: ${data.type}`, 'info');
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            this.addDebugLog('WebSocket 연결 해제됨', 'warning');
            this.updateConnectionStatus(false);
            setTimeout(() => this.initializeWebSocket(), this.config.reconnectInterval);
        };
        
        this.ws.onerror = (error) => {
            this.addDebugLog(`WebSocket 오류: ${error}`, 'error');
            this.updateConnectionStatus(false);
        };
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'welcome':
                this.addDebugLog(`서버 환영 메시지: ${data.message}`, 'success');
                break;
                
            case 'analysis_progress':
                if (data.job_id === this.currentJobId) {
                    this.updateProgress(data.progress, data.processed, data.total);
                }
                break;
                
            case 'analysis_completed':
                if (data.job_id === this.currentJobId) {
                    this.updateProgress(100, data.total_processed, data.total_processed);
                    this.showNotification(`분석이 완료되었습니다! 평균 점수: ${data.average_score}점`, 'success');
                    setTimeout(() => {
                        this.loadRecentJobs();
                    }, 1000);
                }
                break;
                
            case 'analysis_failed':
                if (data.job_id === this.currentJobId) {
                    this.showNotification('분석 중 오류가 발생했습니다: ' + data.error, 'error');
                    this.resetAnalysisButton();
                }
                break;
                
            default:
                this.addDebugLog(`알 수 없는 메시지 타입: ${data.type}`, 'warning');
        }
    }
    
    updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        if (statusIndicator) {
            if (connected) {
                statusIndicator.className = 'status-good';
                statusIndicator.textContent = '연결됨';
            } else {
                statusIndicator.className = 'status-error';
                statusIndicator.textContent = '연결 해제';
            }
        }
    }
    
    // 📁 파일 처리
    triggerFileSelect() {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.click();
        }
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.addDebugLog(`파일 선택: ${file.name}`, 'info');
            this.handleFile(file);
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
    }
    
    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.addDebugLog(`드래그앤드롭 파일: ${files[0].name}`, 'info');
            this.handleFile(files[0]);
        }
    }
    
    handleFile(file) {
        // 파일 크기 검증
        if (file.size > this.config.maxFileSize) {
            this.showNotification(`파일 크기가 ${this.formatFileSize(this.config.maxFileSize)}를 초과합니다.`, 'error');
            return;
        }
        
        // 파일 형식 검증
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.config.allowedFileTypes.includes(fileExtension)) {
            this.showNotification('지원하지 않는 파일 형식입니다. Excel 또는 CSV 파일을 선택해주세요.', 'error');
            return;
        }
        
        this.selectedFile = file;
        this.updateFileInfo(file);
        this.uploadFile(file);
    }
    
    updateFileInfo(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileInfo = document.getElementById('fileInfo');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
        if (fileInfo) fileInfo.style.display = 'block';
        if (analyzeBtn) analyzeBtn.disabled = false;
        
        this.addDebugLog(`파일 정보 업데이트: ${file.name} (${this.formatFileSize(file.size)})`, 'success');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const fileStatus = document.getElementById('fileStatus');
        if (fileStatus) fileStatus.textContent = '업로드 중...';
        
        this.addDebugLog('파일 업로드 시작', 'info');
        const uploadStartTime = Date.now();
        
        try {
            const response = await fetch('/upload/upload/', {
                method: 'POST',
                body: formData
            });
            
            const uploadTime = Date.now() - uploadStartTime;
            this.addDebugLog(`업로드 응답: ${response.status} (${uploadTime}ms)`, 'info');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.addDebugLog(`업로드 완료: 파일 ID = ${data.id}`, 'success');
            
            if (data.id) {
                this.selectedFile.fileId = data.id;
                if (fileStatus) {
                    fileStatus.textContent = `업로드 완료 (${data.total_records || '?'}건 데이터)`;
                }
                this.showNotification('파일이 성공적으로 업로드되었습니다.', 'success');
            } else {
                throw new Error(data.detail || '업로드 실패: 파일 ID를 받지 못했습니다');
            }
        } catch (error) {
            this.addDebugLog(`업로드 오류: ${error.message}`, 'error');
            if (fileStatus) fileStatus.textContent = '업로드 실패';
            this.showNotification('파일 업로드 중 오류: ' + error.message, 'error');
        }
    }
    
    // 🧠 분석 시작
    async startAnalysis() {
        this.addDebugLog('=== AI 분석 프로세스 시작 ===', 'info');
        
        if (!this.selectedFile || !this.selectedFile.fileId) {
            this.showNotification('먼저 파일을 업로드해주세요.', 'error');
            return;
        }
        
        const analysisData = {
            file_id: this.selectedFile.fileId,
            sample_size: 10,
            analysis_mode: 'hybrid',
            enable_ai_feedback: false,
            openai_model: 'gpt-3.5-turbo',
            max_tokens: 1200
        };
        
        this.addDebugLog(`분석 요청 데이터: ${JSON.stringify(analysisData, null, 2)}`, 'info');
        
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.classList.add('loading');
        }
        
        this.updateProgress(0, 0, analysisData.sample_size, '분석 시작 중...');
        
        try {
            await this.sendAnalysisRequest(analysisData);
        } catch (error) {
            this.addDebugLog(`분석 시작 오류: ${error.message}`, 'error');
            this.showNotification('분석 시작 중 오류: ' + error.message, 'error');
            this.resetAnalysisButton();
        }
    }
    
    async sendAnalysisRequest(analysisData) {
        const analysisStartTime = Date.now();
        
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('요청 타임아웃')), 30000);
        });
        
        const fetchPromise = fetch('/analysis/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(analysisData)
        });
        
        const response = await Promise.race([fetchPromise, timeoutPromise]);
        
        const responseTime = Date.now() - analysisStartTime;
        this.addDebugLog(`분석 API 응답 시간: ${responseTime}ms, 상태: ${response.status}`, 'info');
        
        if (!response.ok) {
            const text = await response.text();
            this.addDebugLog(`분석 API 오류 응답: ${text}`, 'error');
            
            try {
                const errorData = JSON.parse(text);
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            } catch (jsonError) {
                throw new Error(`HTTP ${response.status}: ${text}`);
            }
        }
        
        const data = await response.json();
        this.addDebugLog(`분석 시작 성공: Job ID = ${data.job_id}`, 'success');
        
        if (data.job_id) {
            this.currentJobId = data.job_id;
            this.showNotification('AI 분석이 시작되었습니다. 실시간으로 진행상황을 확인할 수 있습니다.', 'success');
            this.updateProgress(0, 0, analysisData.sample_size, '분석 진행 중...');
        } else {
            throw new Error(data.detail || '분석 시작 실패: Job ID를 받지 못했습니다');
        }
    }
    
    resetAnalysisButton() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('loading');
        }
        this.updateProgress(0, 0, 0, '대기 중');
    }
    
    updateProgress(percent, processed, total, text) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
        
        if (progressText) {
            progressText.textContent = text || `진행률: ${percent.toFixed(1)}% (${processed}/${total})`;
        }
        
        this.addDebugLog(`진행률 업데이트: ${percent.toFixed(1)}% (${processed}/${total})`, 'info');
    }
    
    // 📊 결과 관리
    async loadRecentJobs() {
        this.addDebugLog('최근 작업 목록 조회 시작', 'info');
        
        try {
            const response = await fetch('/analysis/jobs');
            this.addDebugLog(`작업 목록 응답: ${response.status}`, 'info');
            
            const jobs = await response.json();
            this.addDebugLog(`작업 수: ${jobs.length}`, 'info');
            
            this.displayJobs(jobs);
        } catch (error) {
            this.addDebugLog(`작업 목록 조회 오류: ${error.message}`, 'error');
            this.displayEmptyJobsState();
        }
    }
    
    displayJobs(jobs) {
        const container = document.getElementById('recentJobs');
        if (!container) return;
        
        if (jobs.length === 0) {
            this.displayEmptyJobsState();
            return;
        }
        
        let html = '<h3><i class="fas fa-history"></i> 최근 분석 작업</h3>';
        
        jobs.forEach((job, index) => {
            const createdDate = new Date(job.created_at || Date.now()).toLocaleString();
            const statusIcon = this.getJobStatusIcon(job.status);
            const statusColor = this.getJobStatusColor(job.status);
            
            html += `
                <div class="job-item" style="animation-delay: ${index * 0.1}s;">
                    <div class="job-info">
                        <div class="job-title">
                            <i class="fas fa-file-excel" style="color: var(--primary-color);"></i>
                            ${job.filename || 'Unknown File'}
                        </div>
                        <div class="job-meta">
                            <i class="${statusIcon}" style="color: ${statusColor};"></i>
                            ${job.processed || 0}명 분석 완료 • ${createdDate}
                        </div>
                    </div>
                    <div>
                        <button class="button" onclick="airissApp.viewResults('${job.job_id}')">
                            <i class="fas fa-chart-bar"></i> 결과 보기
                        </button>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    displayEmptyJobsState() {
        const container = document.getElementById('recentJobs');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #666;">
                    <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 15px; color: #ccc;"></i>
                    <h3>최근 분석 작업이 없습니다</h3>
                    <p>파일을 업로드하여 첫 번째 분석을 시작해보세요!</p>
                </div>
            `;
        }
    }
    
    getJobStatusIcon(status) {
        const icons = {
            'completed': 'fas fa-check-circle',
            'failed': 'fas fa-times-circle',
            'running': 'fas fa-clock',
            'pending': 'fas fa-hourglass-start'
        };
        return icons[status] || 'fas fa-question-circle';
    }
    
    getJobStatusColor(status) {
        const colors = {
            'completed': 'var(--success-color)',
            'failed': 'var(--danger-color)',
            'running': 'var(--warning-color)',
            'pending': 'var(--primary-color)'
        };
        return colors[status] || '#666';
    }
    
    viewResults(jobId) {
        this.addDebugLog(`결과 보기: ${jobId}`, 'info');
        this.showNotification('결과 페이지로 이동합니다...', 'info');
        window.open(`/docs#/analysis/get_analysis_results_analysis_results__job_id__get`, '_blank');
    }
    
    // 🛠️ 시스템 테스트
    async testAnalysisAPI() {
        this.addDebugLog('=== 시스템 종합 테스트 시작 ===', 'info');
        
        const testBtn = document.getElementById('testApiBtn');
        if (testBtn) {
            testBtn.disabled = true;
            testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 테스트 중...';
        }
        
        const tests = [
            { name: 'Health Check', url: '/health' },
            { name: 'Analysis Engine', url: '/health/analysis' },
            { name: 'Database', url: '/health/db' }
        ];
        
        let successCount = 0;
        
        try {
            for (const test of tests) {
                try {
                    const response = await fetch(test.url);
                    const data = await response.json();
                    
                    if (response.ok && data.status === 'healthy') {
                        this.addDebugLog(`✅ ${test.name}: ${data.status}`, 'success');
                        successCount++;
                    } else {
                        this.addDebugLog(`❌ ${test.name}: ${data.status || 'error'}`, 'error');
                    }
                } catch (error) {
                    this.addDebugLog(`❌ ${test.name}: ${error.message}`, 'error');
                }
            }
            
            if (successCount === tests.length) {
                this.showNotification(`시스템 테스트 완료! 모든 컴포넌트(${tests.length})가 정상 작동 중입니다.`, 'success');
            } else {
                this.showNotification(`시스템 테스트 완료. ${successCount}/${tests.length} 컴포넌트가 정상입니다.`, 'warning');
            }
            
            this.addDebugLog('=== 시스템 테스트 완료 ===', 'success');
        } catch (error) {
            this.addDebugLog(`시스템 테스트 실패: ${error.message}`, 'error');
            this.showNotification('시스템 테스트 중 오류 발생: ' + error.message, 'error');
        } finally {
            if (testBtn) {
                testBtn.disabled = false;
                testBtn.innerHTML = '<i class="fas fa-tools"></i> 시스템 테스트';
            }
        }
    }
    
    // 🔔 알림 시스템
    showNotification(message, type = 'success', timeout = null) {
        const notification = document.getElementById('notification');
        const text = document.getElementById('notificationText');
        const icon = document.getElementById('notificationIcon');
        
        if (!notification || !text) return;
        
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-times-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        
        text.textContent = message;
        if (icon) icon.className = iconMap[type] || iconMap.success;
        notification.className = 'notification ' + type + ' show';
        
        // 자동 숨김
        setTimeout(() => {
            this.hideNotification();
        }, timeout || this.config.notificationTimeout);
        
        this.addDebugLog(`알림: ${message}`, type);
    }
    
    hideNotification() {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.classList.remove('show');
        }
    }
    
    // 🐛 디버깅 시스템
    addDebugLog(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        
        // 콘솔에 출력
        const logMethod = console[type] || console.log;
        logMethod(`[AIRISS v4.0] ${message}`);
    }
    
    // ⌨️ 키보드 단축키
    handleKeyboardShortcuts(event) {
        // Ctrl + U: 파일 업로드
        if (event.ctrlKey && event.key === 'u') {
            event.preventDefault();
            this.triggerFileSelect();
        }
        
        // Escape: 알림 숨기기
        if (event.key === 'Escape') {
            this.hideNotification();
        }
    }
    
    // 📱 유틸리티 함수들
    async updateConnectionCount() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            const count = data.components?.connection_count || '0';
            
            const connectionCount = document.getElementById('connectionCount');
            if (connectionCount) {
                connectionCount.textContent = count;
            }
            
            this.addDebugLog(`연결 수 업데이트: ${count}`, 'info');
        } catch (error) {
            const connectionCount = document.getElementById('connectionCount');
            if (connectionCount) {
                connectionCount.textContent = '?';
            }
            this.addDebugLog(`연결 수 업데이트 실패: ${error.message}`, 'error');
        }
    }
    
    showSampleData() {
        this.addDebugLog('샘플 데이터 생성 및 다운로드', 'info');
        
        const sampleData = `UID,이름,의견,성과등급,KPI점수
EMP001,김철수,매우 열심히 업무에 임하고 동료들과 원활한 소통을 하고 있습니다.,A,85
EMP002,이영희,창의적인 아이디어로 프로젝트를 성공적으로 이끌었습니다.,B+,78
EMP003,박민수,시간 관리와 업무 효율성 측면에서 개선이 필요합니다.,C,65
EMP004,최영수,고객과의 소통이 뛰어나고 문제 해결 능력이 우수합니다.,A,92
EMP005,한지민,팀워크가 좋고 협업 능력이 뛰어난 직원입니다.,B+,80`;
        
        const blob = new Blob([sampleData], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'AIRISS_샘플데이터.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification('AIRISS 샘플 데이터가 다운로드되었습니다.', 'success');
        this.addDebugLog('샘플 데이터 다운로드 완료', 'success');
    }
    
    handleOnlineStatus(isOnline) {
        this.isOnline = isOnline;
        
        if (isOnline) {
            this.addDebugLog('온라인 상태로 변경됨', 'success');
        } else {
            this.addDebugLog('오프라인 상태로 변경됨', 'warning');
            this.showNotification('오프라인 모드입니다.', 'warning');
        }
    }
    
    // 🧹 정리
    cleanup() {
        if (this.ws) {
            this.ws.close();
            this.addDebugLog('WebSocket 연결 정리 완료', 'info');
        }
        
        if (this.resultsChart) {
            this.resultsChart.destroy();
        }
    }
}

// 전역 인스턴스 생성
let airissApp;

// DOM 로드 시 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    airissApp = new AIRISSApp();
});

// 전역 함수들 (기존 HTML의 onclick 이벤트 호환성을 위해)
window.startAnalysis = () => airissApp?.startAnalysis();
window.testAnalysisAPI = () => airissApp?.testAnalysisAPI();
window.loadRecentJobs = () => airissApp?.loadRecentJobs();
window.showSampleData = () => airissApp?.showSampleData();
window.viewResults = (jobId) => airissApp?.viewResults(jobId);
