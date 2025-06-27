// performance_forecast.js - 성과 예측 시각화 컴포넌트

class PerformanceForecastChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.chart = null;
        this.init();
    }
    
    init() {
        // 초기 차트 설정
        this.createChart();
    }
    
    createChart() {
        // 시간축 레이블 (과거 6개월 + 현재 + 미래 6개월)
        const labels = [
            '6개월 전', '5개월 전', '4개월 전', '3개월 전', '2개월 전', '1개월 전',
            '현재',
            '1개월 후', '2개월 후', '3개월 후', '4개월 후', '5개월 후', '6개월 후'
        ];
        
        // 그라데이션 생성
        const gradient = this.ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(255, 87, 34, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 87, 34, 0.2)');
        
        const futureGradient = this.ctx.createLinearGradient(0, 0, 0, 400);
        futureGradient.addColorStop(0, 'rgba(76, 175, 80, 0.8)');
        futureGradient.addColorStop(1, 'rgba(76, 175, 80, 0.2)');
        
        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '실제 성과',
                    data: [72, 74, 73, 75, 78, 80, 82, null, null, null, null, null, null],
                    borderColor: 'rgba(255, 87, 34, 1)',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.2
                }, {
                    label: '예측 성과',
                    data: [null, null, null, null, null, null, 82, 84, 86, 87, 88, 89, 90],
                    borderColor: 'rgba(76, 175, 80, 1)',
                    backgroundColor: futureGradient,
                    borderWidth: 3,
                    borderDash: [5, 5],
                    pointRadius: 6,
                    pointHoverRadius: 8,
                    tension: 0.2
                }, {
                    label: '신뢰구간 상한',
                    data: [null, null, null, null, null, null, 82, 86, 89, 91, 93, 94, 95],
                    borderColor: 'rgba(76, 175, 80, 0.3)',
                    backgroundColor: 'transparent',
                    borderWidth: 1,
                    borderDash: [2, 2],
                    pointRadius: 0,
                    fill: false
                }, {
                    label: '신뢰구간 하한',
                    data: [null, null, null, null, null, null, 82, 82, 83, 83, 83, 84, 85],
                    borderColor: 'rgba(76, 175, 80, 0.3)',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 1,
                    borderDash: [2, 2],
                    pointRadius: 0,
                    fill: '+1' // 상한과 하한 사이 채우기
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'AI 기반 성과 예측 분석',
                        font: {
                            size: 18,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12
                            },
                            filter: function(item) {
                                // 신뢰구간은 범례에서 숨김
                                return !item.text.includes('신뢰구간');
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            title: function(context) {
                                return context[0].label;
                            },
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (context.parsed.y !== null) {
                                    label += ': ' + context.parsed.y + '점';
                                    
                                    // 예측 구간에 대한 추가 정보
                                    if (context.dataIndex > 6 && context.dataset.label === '예측 성과') {
                                        const confidence = 85 - (context.dataIndex - 7) * 2; // 시간이 지날수록 신뢰도 감소
                                        label += ` (신뢰도: ${confidence}%)`;
                                    }
                                }
                                return label;
                            }
                        }
                    },
                    annotation: {
                        annotations: {
                            currentLine: {
                                type: 'line',
                                xMin: 6,
                                xMax: 6,
                                borderColor: 'rgba(255, 0, 0, 0.5)',
                                borderWidth: 2,
                                borderDash: [6, 6],
                                label: {
                                    enabled: true,
                                    content: '현재',
                                    position: 'start',
                                    backgroundColor: 'rgba(255, 0, 0, 0.8)',
                                    color: 'white',
                                    font: {
                                        size: 12,
                                        weight: 'bold'
                                    }
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: '시간',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: '성과 점수',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        },
                        min: 60,
                        max: 100,
                        ticks: {
                            stepSize: 10
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    updatePrediction(employeeData) {
        // 직원별 예측 데이터 업데이트
        const historicalScores = employeeData.historical || [72, 74, 73, 75, 78, 80, 82];
        const currentScore = employeeData.current || 82;
        const prediction = employeeData.prediction || {
            scores: [84, 86, 87, 88, 89, 90],
            upper: [86, 89, 91, 93, 94, 95],
            lower: [82, 83, 83, 83, 84, 85]
        };
        
        // 차트 데이터 업데이트
        this.chart.data.datasets[0].data = [...historicalScores, null, null, null, null, null, null];
        this.chart.data.datasets[1].data = [
            ...Array(historicalScores.length - 1).fill(null), 
            currentScore, 
            ...prediction.scores
        ];
        this.chart.data.datasets[2].data = [
            ...Array(historicalScores.length).fill(null),
            ...prediction.upper
        ];
        this.chart.data.datasets[3].data = [
            ...Array(historicalScores.length).fill(null),
            ...prediction.lower
        ];
        
        this.chart.update();
    }
    
    showInsights(analysisResult) {
        // 예측 인사이트 표시
        const insights = document.createElement('div');
        insights.className = 'forecast-insights';
        insights.innerHTML = `
            <h4><i class="fas fa-lightbulb"></i> AI 예측 인사이트</h4>
            <div class="insight-cards">
                <div class="insight-card ${this.getTrendClass(analysisResult.trend)}">
                    <i class="fas fa-trending-${analysisResult.trend}"></i>
                    <span class="insight-label">예상 트렌드</span>
                    <span class="insight-value">${this.getTrendText(analysisResult.trend)}</span>
                </div>
                <div class="insight-card">
                    <i class="fas fa-percentage"></i>
                    <span class="insight-label">성공 확률</span>
                    <span class="insight-value">${analysisResult.success_probability}%</span>
                </div>
                <div class="insight-card ${analysisResult.turnover_risk > 30 ? 'warning' : ''}">
                    <i class="fas fa-door-open"></i>
                    <span class="insight-label">이직 위험도</span>
                    <span class="insight-value">${analysisResult.turnover_risk}%</span>
                </div>
                <div class="insight-card">
                    <i class="fas fa-graduation-cap"></i>
                    <span class="insight-label">개발 우선순위</span>
                    <span class="insight-value">${analysisResult.development_priority || '리더십'}</span>
                </div>
            </div>
            <div class="action-recommendations">
                <h5><i class="fas fa-tasks"></i> 권장 조치사항</h5>
                <ul>
                    ${this.generateRecommendations(analysisResult).map(r => `<li>${r}</li>`).join('')}
                </ul>
            </div>
        `;
        
        // 차트 아래에 인사이트 추가
        this.canvas.parentElement.appendChild(insights);
    }
    
    getTrendClass(trend) {
        switch(trend) {
            case 'up': return 'positive';
            case 'down': return 'negative';
            default: return 'neutral';
        }
    }
    
    getTrendText(trend) {
        switch(trend) {
            case 'up': return '상승 예상';
            case 'down': return '하락 우려';
            default: return '현상 유지';
        }
    }
    
    generateRecommendations(analysis) {
        const recommendations = [];
        
        if (analysis.trend === 'up') {
            recommendations.push('현재의 긍정적 모멘텀을 유지하기 위한 지속적 피드백 제공');
            recommendations.push('도전적인 프로젝트 배정으로 성장 기회 확대');
        } else if (analysis.trend === 'down') {
            recommendations.push('1:1 면담을 통한 어려움 파악 및 지원 방안 모색');
            recommendations.push('멘토링 프로그램 연결 및 역량 개발 계획 수립');
        }
        
        if (analysis.turnover_risk > 30) {
            recommendations.push('경력 개발 경로 논의 및 보상 체계 검토');
            recommendations.push('업무 만족도 향상을 위한 역할 재조정 고려');
        }
        
        if (analysis.development_priority) {
            recommendations.push(`${analysis.development_priority} 역량 강화를 위한 교육 프로그램 추천`);
        }
        
        return recommendations;
    }
}

// CSS 스타일 추가
const forecastStyles = `
<style>
.forecast-insights {
    margin-top: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
}

.forecast-insights h4 {
    color: #FF5722;
    margin-bottom: 20px;
}

.insight-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.insight-card {
    background: white;
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.insight-card:hover {
    transform: translateY(-2px);
}

.insight-card i {
    font-size: 2rem;
    margin-bottom: 10px;
    color: #FF5722;
}

.insight-card.positive i {
    color: #4CAF50;
}

.insight-card.negative i {
    color: #f44336;
}

.insight-card.warning {
    border-left: 4px solid #FF9800;
}

.insight-label {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-bottom: 5px;
}

.insight-value {
    display: block;
    font-size: 1.3rem;
    font-weight: bold;
    color: #333;
}

.action-recommendations {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 4px solid #FF5722;
}

.action-recommendations h5 {
    color: #333;
    margin-bottom: 15px;
}

.action-recommendations ul {
    list-style: none;
    padding-left: 0;
}

.action-recommendations li {
    padding-left: 25px;
    margin-bottom: 10px;
    position: relative;
}

.action-recommendations li:before {
    content: "→";
    position: absolute;
    left: 0;
    color: #FF5722;
    font-weight: bold;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', forecastStyles);