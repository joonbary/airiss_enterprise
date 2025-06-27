// bias_monitoring.js - 실시간 편향성 모니터링 위젯

class BiasMonitoringWidget {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.biasData = {
            gender: { score: 100, trend: 'stable' },
            age: { score: 100, trend: 'stable' },
            appearance: { score: 100, trend: 'stable' },
            overall: { score: 100, status: 'fair' }
        };
        this.init();
    }
    
    init() {
        this.render();
        this.startMonitoring();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="bias-monitor-widget">
                <h4><i class="fas fa-balance-scale"></i> 공정성 모니터링</h4>
                <div class="bias-metrics">
                    <div class="metric-item">
                        <span class="metric-label">성별 편향</span>
                        <div class="metric-bar">
                            <div class="metric-fill gender-fill" style="width: ${this.biasData.gender.score}%"></div>
                        </div>
                        <span class="metric-score">${this.biasData.gender.score}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">연령 편향</span>
                        <div class="metric-bar">
                            <div class="metric-fill age-fill" style="width: ${this.biasData.age.score}%"></div>
                        </div>
                        <span class="metric-score">${this.biasData.age.score}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">외모 편향</span>
                        <div class="metric-bar">
                            <div class="metric-fill appearance-fill" style="width: ${this.biasData.appearance.score}%"></div>
                        </div>
                        <span class="metric-score">${this.biasData.appearance.score}%</span>
                    </div>
                </div>
                <div class="bias-status ${this.biasData.overall.status}">
                    <i class="fas fa-${this.getStatusIcon()}"></i>
                    전체 공정성: ${this.getStatusText()}
                </div>
            </div>
        `;
    }
    
    updateBiasScore(biasAnalysis) {
        // 편향성 분석 결과 업데이트
        if (biasAnalysis.gender_bias) {
            this.biasData.gender.score = Math.max(0, this.biasData.gender.score - 20);
        }
        if (biasAnalysis.age_bias) {
            this.biasData.age.score = Math.max(0, this.biasData.age.score - 15);
        }
        if (biasAnalysis.appearance_bias) {
            this.biasData.appearance.score = Math.max(0, this.biasData.appearance.score - 30);
        }
        
        // 전체 공정성 점수 계산
        this.biasData.overall.score = biasAnalysis.fairness_score || 
            (this.biasData.gender.score + this.biasData.age.score + this.biasData.appearance.score) / 3;
        
        // 상태 업데이트
        if (this.biasData.overall.score >= 80) {
            this.biasData.overall.status = 'fair';
        } else if (this.biasData.overall.score >= 60) {
            this.biasData.overall.status = 'warning';
        } else {
            this.biasData.overall.status = 'danger';
        }
        
        this.render();
        
        // 경고 알림
        if (this.biasData.overall.score < 80) {
            this.showBiasWarning(biasAnalysis.bias_details);
        }
    }
    
    showBiasWarning(details) {
        const warningMsg = details.map(d => `${d.type}: ${d.description}`).join(', ');
        showNotification(`⚠️ 편향성 감지: ${warningMsg}`, 'warning');
    }
    
    getStatusIcon() {
        switch(this.biasData.overall.status) {
            case 'fair': return 'check-circle';
            case 'warning': return 'exclamation-triangle';
            case 'danger': return 'times-circle';
            default: return 'question-circle';
        }
    }
    
    getStatusText() {
        switch(this.biasData.overall.status) {
            case 'fair': return '공정함 ✅';
            case 'warning': return '주의 필요 ⚠️';
            case 'danger': return '편향 위험 ❌';
            default: return '분석 중...';
        }
    }
    
    startMonitoring() {
        // WebSocket으로 실시간 모니터링
        if (window.ws) {
            window.ws.addEventListener('message', (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'bias_analysis' && data.bias_analysis) {
                    this.updateBiasScore(data.bias_analysis);
                }
            });
        }
    }
}

// CSS 스타일 추가
const biasMonitorStyles = `
<style>
.bias-monitor-widget {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin: 20px 0;
}

.bias-monitor-widget h4 {
    color: #1a73e8;
    margin-bottom: 20px;
    font-size: 1.2rem;
}

.bias-metrics {
    margin-bottom: 20px;
}

.metric-item {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.metric-label {
    width: 120px;
    font-size: 0.9rem;
    color: #666;
}

.metric-bar {
    flex: 1;
    height: 20px;
    background: #f0f0f0;
    border-radius: 10px;
    margin: 0 10px;
    overflow: hidden;
}

.metric-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #45a049);
    transition: width 0.5s ease;
    border-radius: 10px;
}

.metric-fill.gender-fill {
    background: linear-gradient(90deg, #2196F3, #1976D2);
}

.metric-fill.age-fill {
    background: linear-gradient(90deg, #FF9800, #F57C00);
}

.metric-fill.appearance-fill {
    background: linear-gradient(90deg, #9C27B0, #7B1FA2);
}

.metric-score {
    width: 50px;
    text-align: right;
    font-weight: bold;
    color: #333;
}

.bias-status {
    text-align: center;
    padding: 15px;
    border-radius: 8px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.bias-status.fair {
    background: #E8F5E9;
    color: #2E7D32;
}

.bias-status.warning {
    background: #FFF3E0;
    color: #F57C00;
}

.bias-status.danger {
    background: #FFEBEE;
    color: #C62828;
}
</style>
`;

// 페이지에 스타일 추가
document.head.insertAdjacentHTML('beforeend', biasMonitorStyles);