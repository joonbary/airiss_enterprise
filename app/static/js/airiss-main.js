// AIRISS v4.1 Enhanced JavaScript

// 전역 변수
let selectedFile = null;
let currentJobId = null;
let ws = null;
let debugMode = false;
let resultsChart = null;
let tourStep = 0;
let lastAnalysisResult = null;

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

// 🌐 WebSocket 연결 시스템
function connectWebSocket() {
    const clientId = 'enhanced-ui-' + Math.random().toString(36).substr(2, 9);
    addDebugLog(`WebSocket 연결 시도: ${clientId}`, 'info');
    
    // 동적으로 호스트와 포트 가져오기
    const wsHost = window.location.hostname || 'localhost';
    const wsPort = window.location.port || '8002';
    ws = new WebSocket(`ws://${wsHost}:${wsPort}/ws/${clientId}?channels=analysis,alerts`);
    
    ws.onopen = () => {
        addDebugLog('WebSocket 연결 성공', 'success');
        updateConnectionCount();
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        addDebugLog(`WebSocket 메시지 수신: ${data.type}`, 'info');
        handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
        addDebugLog('WebSocket 연결 해제됨', 'warning');
        setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        addDebugLog(`WebSocket 오류: ${error}`, 'error');
    };
}

function handleWebSocketMessage(data) {
    if (data.type === 'analysis_progress' && data.job_id === currentJobId) {
        updateProgress(data.progress, data.processed, data.total);
    } else if (data.type === 'analysis_completed' && data.job_id === currentJobId) {
        updateProgress(100, data.total_processed, data.total_processed);
        showNotification(`분석이 완료되었습니다! 평균 점수: ${data.average_score}점`, 'success');
        setTimeout(() => {
            loadRecentJobs();
            showResultsChart();
        }, 1000);
    } else if (data.type === 'analysis_failed' && data.job_id === currentJobId) {
        showNotification('분석 중 오류가 발생했습니다: ' + data.error, 'error');
        resetAnalysisButton();
    }
}

function updateConnectionCount() {
    fetch('/health')
    .then(response => response.json())
    .then(data => {
        const count = data.components?.connection_count || '0';
        document.getElementById('connectionCount').textContent = count;
        addDebugLog(`연결 수 업데이트: ${count}`, 'info');
    })
    .catch(error => {
        document.getElementById('connectionCount').textContent = '?';
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
    
    fetch('/upload/upload/', {
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
    addDebugLog('=== AI 분석 프로세스 시작 ===', 'info');
    
    if (!selectedFile || !selectedFile.fileId) {
        showNotification('먼저 파일을 업로드해주세요.', 'error');
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
                <div>
                    <button class="button" onclick="viewResults('${job.job_id}')" style="padding: 8px 16px; font-size: 0.9rem;">
                        <i class="fas fa-chart-bar"></i> 결과 보기
                    </button>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function viewResults(jobId) {
    addDebugLog(`결과 보기: ${jobId}`, 'info');
    showNotification('결과 페이지로 이동합니다...', 'info');
    window.open(`/docs#/analysis/get_analysis_results_analysis_results__job_id__get`, '_blank');
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

// 🚀 페이지 초기화
document.addEventListener('DOMContentLoaded', function() {
    addDebugLog('AIRISS v4.1 Enhanced UI 초기화 시작', 'info');
    
    // WebSocket 연결
    connectWebSocket();
    
    // 연결 상태 업데이트
    updateConnectionCount();
    
    // 최근 작업 로드
    loadRecentJobs();
    
    // 정기 업데이트 (30초마다)
    setInterval(() => {
        updateConnectionCount();
    }, 30000);
    
    // 온보딩 체크 (첫 방문자용)
    const hasVisited = localStorage.getItem('airiss_visited');
    if (!hasVisited) {
        setTimeout(() => {
            showOnboarding();
            localStorage.setItem('airiss_visited', 'true');
        }, 2000);
    }
    
    addDebugLog('초기화 완료 - AIRISS v4.1 Enhanced 시스템 준비됨', 'success');
    showNotification('AIRISS v4.1 Enhanced가 시작되었습니다! 파일을 업로드하여 AI 분석을 시작해보세요.', 'info');
});

// 페이지 언로드 시 WebSocket 정리
window.addEventListener('beforeunload', function() {
    if (ws) {
        ws.close();
        addDebugLog('WebSocket 연결 정리 완료', 'info');
    }
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
    
    // F1: 도움말
    if (e.key === 'F1') {
        e.preventDefault();
        showOnboarding();
    }
});
