# app/services/bias_detection/bias_detector.py
"""
AIRISS v4.0 편향 탐지 시스템
성별, 연령, 부서별 공정성 자동 검증
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BiasDetector:
    """AI 평가 편향 탐지 및 공정성 검증 시스템"""
    
    def __init__(self):
        self.thresholds = {
            'statistical_parity': 0.1,  # 10% 이내 차이 허용
            'equalized_odds': 0.15,     # 15% 이내 차이 허용
            'cohen_d': 0.2,             # Small effect size 기준
            'p_value': 0.05             # 통계적 유의성 기준
        }
        
        self.protected_attributes = ['성별', '연령대', '부서', '직급']
        
        logger.info("✅ AIRISS 편향 탐지 시스템 초기화 완료")
    
    def detect_bias(self, analysis_results: pd.DataFrame) -> Dict[str, any]:
        """종합적인 편향 탐지 수행"""
        
        bias_report = {
            'summary': {
                'total_analyzed': len(analysis_results),
                'bias_detected': False,
                'risk_level': 'LOW',
                'timestamp': datetime.now().isoformat()
            },
            'detailed_analysis': {},
            'recommendations': []
        }
        
        # 각 보호 속성별 편향 분석
        for attr in self.protected_attributes:
            if attr in analysis_results.columns:
                attr_analysis = self._analyze_attribute_bias(
                    analysis_results, 
                    attr, 
                    'hybrid_score'
                )
                bias_report['detailed_analysis'][attr] = attr_analysis
                
                if attr_analysis['bias_detected']:
                    bias_report['summary']['bias_detected'] = True
        
        # 교차 편향 분석 (예: 성별 x 연령대)
        if '성별' in analysis_results.columns and '연령대' in analysis_results.columns:
            intersectional_bias = self._analyze_intersectional_bias(
                analysis_results, 
                ['성별', '연령대'], 
                'hybrid_score'
            )
            bias_report['detailed_analysis']['intersectional'] = intersectional_bias
        
        # 위험 수준 평가
        bias_report['summary']['risk_level'] = self._assess_risk_level(bias_report)
        
        # 권고사항 생성
        bias_report['recommendations'] = self._generate_recommendations(bias_report)
        
        return bias_report
    
    def _analyze_attribute_bias(self, 
                               df: pd.DataFrame, 
                               attribute: str, 
                               score_column: str) -> Dict:
        """특정 속성에 대한 편향 분석"""
        
        groups = df.groupby(attribute)[score_column]
        group_stats = groups.agg(['mean', 'std', 'count']).to_dict('index')
        
        # 통계적 형평성 (Statistical Parity) 계산
        means = [stats['mean'] for stats in group_stats.values()]
        max_diff = max(means) - min(means)
        avg_mean = np.mean(means)
        parity_ratio = max_diff / avg_mean if avg_mean > 0 else 0
        
        # ANOVA 검정
        group_scores = [group[score_column].values for name, group in df.groupby(attribute)]
        f_stat, p_value = stats.f_oneway(*group_scores) if len(group_scores) > 1 else (0, 1)
        
        # Cohen's d 효과 크기 계산 (최대/최소 그룹 간)
        if len(means) >= 2:
            sorted_groups = sorted(group_stats.items(), key=lambda x: x[1]['mean'])
            low_group = df[df[attribute] == sorted_groups[0][0]][score_column]
            high_group = df[df[attribute] == sorted_groups[-1][0]][score_column]
            cohen_d = self._calculate_cohen_d(low_group, high_group)
        else:
            cohen_d = 0
        
        # 편향 판정
        bias_detected = (
            parity_ratio > self.thresholds['statistical_parity'] or
            p_value < self.thresholds['p_value'] or
            abs(cohen_d) > self.thresholds['cohen_d']
        )
        
        return {
            'bias_detected': bias_detected,
            'group_statistics': group_stats,
            'statistical_tests': {
                'parity_ratio': round(parity_ratio, 3),
                'anova_f_stat': round(f_stat, 3),
                'p_value': round(p_value, 4),
                'cohen_d': round(cohen_d, 3)
            },
            'interpretation': self._interpret_bias_results(
                parity_ratio, p_value, cohen_d, attribute
            )
        }
    
    def _analyze_intersectional_bias(self, 
                                    df: pd.DataFrame, 
                                    attributes: List[str], 
                                    score_column: str) -> Dict:
        """교차 속성 편향 분석 (예: 여성 x 40대)"""
        
        # 교차 그룹 생성
        df['intersectional_group'] = df[attributes].apply(
            lambda x: '_'.join(x.astype(str)), axis=1
        )
        
        # 교차 그룹별 분석
        intersectional_analysis = self._analyze_attribute_bias(
            df, 'intersectional_group', score_column
        )
        
        # 가장 불리한 그룹 식별
        group_means = intersectional_analysis['group_statistics']
        worst_group = min(group_means.items(), key=lambda x: x[1]['mean'])[0]
        best_group = max(group_means.items(), key=lambda x: x[1]['mean'])[0]
        
        intersectional_analysis['most_disadvantaged'] = worst_group
        intersectional_analysis['most_advantaged'] = best_group
        intersectional_analysis['gap'] = (
            group_means[best_group]['mean'] - group_means[worst_group]['mean']
        )
        
        return intersectional_analysis
    
    def _calculate_cohen_d(self, group1: pd.Series, group2: pd.Series) -> float:
        """Cohen's d 효과 크기 계산"""
        n1, n2 = len(group1), len(group2)
        var1, var2 = group1.var(), group2.var()
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        # Cohen's d
        if pooled_std > 0:
            return (group1.mean() - group2.mean()) / pooled_std
        return 0
    
    def _assess_risk_level(self, bias_report: Dict) -> str:
        """편향 위험 수준 평가"""
        
        bias_count = sum(
            1 for analysis in bias_report['detailed_analysis'].values()
            if analysis.get('bias_detected', False)
        )
        
        # 교차 편향이 있으면 위험도 상승
        if 'intersectional' in bias_report['detailed_analysis']:
            if bias_report['detailed_analysis']['intersectional'].get('bias_detected'):
                bias_count += 1
        
        if bias_count == 0:
            return 'LOW'
        elif bias_count == 1:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _interpret_bias_results(self, 
                               parity_ratio: float, 
                               p_value: float, 
                               cohen_d: float,
                               attribute: str) -> str:
        """편향 분석 결과 해석"""
        
        interpretations = []
        
        if parity_ratio > self.thresholds['statistical_parity']:
            interpretations.append(
                f"{attribute}별 평균 점수 차이가 {parity_ratio*100:.1f}%로 "
                f"허용 기준({self.thresholds['statistical_parity']*100}%)을 초과합니다."
            )
        
        if p_value < self.thresholds['p_value']:
            interpretations.append(
                f"통계적으로 유의미한 차이가 발견되었습니다 (p={p_value:.4f})."
            )
        
        if abs(cohen_d) > self.thresholds['cohen_d']:
            effect_size = (
                "작은" if abs(cohen_d) < 0.5 else
                "중간" if abs(cohen_d) < 0.8 else
                "큰"
            )
            interpretations.append(
                f"{effect_size} 효과 크기(d={cohen_d:.2f})가 관찰되었습니다."
            )
        
        if not interpretations:
            return f"{attribute}에 대한 유의미한 편향이 발견되지 않았습니다."
        
        return " ".join(interpretations)
    
    def _generate_recommendations(self, bias_report: Dict) -> List[str]:
        """편향 완화를 위한 권고사항 생성"""
        
        recommendations = []
        
        if not bias_report['summary']['bias_detected']:
            recommendations.append(
                "✅ 현재 분석 결과에서 유의미한 편향이 발견되지 않았습니다. "
                "지속적인 모니터링을 권장합니다."
            )
            return recommendations
        
        # 속성별 권고사항
        for attr, analysis in bias_report['detailed_analysis'].items():
            if analysis.get('bias_detected'):
                if attr == '성별':
                    recommendations.append(
                        "⚠️ 성별 편향 완화: 평가 기준에서 성별 중립적 언어 사용을 강화하고, "
                        "다양성 관점의 평가자를 포함시키세요."
                    )
                elif attr == '연령대':
                    recommendations.append(
                        "⚠️ 연령 편향 완화: 세대별 업무 스타일 차이를 인정하고, "
                        "연령 중립적인 성과 지표를 개발하세요."
                    )
                elif attr == '부서':
                    recommendations.append(
                        "⚠️ 부서 편향 완화: 부서별 업무 특성을 반영한 맞춤형 평가 기준을 "
                        "개발하고, 크로스 펑셔널 평가를 도입하세요."
                    )
        
        # 위험 수준별 추가 권고
        risk_level = bias_report['summary']['risk_level']
        if risk_level == 'HIGH':
            recommendations.append(
                "🚨 높은 위험: 즉시 AI 모델 재훈련과 평가 프로세스 전면 검토가 필요합니다. "
                "외부 전문가 자문을 고려하세요."
            )
        elif risk_level == 'MEDIUM':
            recommendations.append(
                "⚡ 중간 위험: 편향 완화 조치를 우선순위로 실행하고, "
                "월별 편향 모니터링을 강화하세요."
            )
        
        # 일반 권고사항
        recommendations.extend([
            "💡 정기적인 편향 감사 실시 (최소 분기별)",
            "💡 다양성 교육 프로그램 강화",
            "💡 AI 평가 결과에 대한 인간 검토 프로세스 강화"
        ])
        
        return recommendations

    def generate_fairness_report(self, 
                                analysis_results: pd.DataFrame,
                                output_format: str = 'html') -> str:
        """공정성 보고서 생성"""
        
        bias_report = self.detect_bias(analysis_results)
        
        if output_format == 'html':
            return self._generate_html_report(bias_report)
        elif output_format == 'json':
            import json
            return json.dumps(bias_report, ensure_ascii=False, indent=2)
        else:
            return str(bias_report)
    
    def _generate_html_report(self, bias_report: Dict) -> str:
        """HTML 형식의 공정성 보고서 생성"""
        
        risk_colors = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#f44336'
        }
        
        risk_color = risk_colors.get(bias_report['summary']['risk_level'], '#666')
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
            <h2 style="color: #FF5722;">🔍 AIRISS v4.0 공정성 분석 보고서</h2>
            
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>📊 요약</h3>
                <p><strong>분석 대상:</strong> {bias_report['summary']['total_analyzed']}명</p>
                <p><strong>편향 탐지:</strong> {'🚨 발견됨' if bias_report['summary']['bias_detected'] else '✅ 발견되지 않음'}</p>
                <p><strong>위험 수준:</strong> <span style="color: {risk_color}; font-weight: bold;">{bias_report['summary']['risk_level']}</span></p>
                <p><strong>분석 시간:</strong> {bias_report['summary']['timestamp']}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <h3>📈 상세 분석 결과</h3>
        """
        
        for attr, analysis in bias_report['detailed_analysis'].items():
            if attr != 'intersectional':
                bias_status = '🚨 편향 발견' if analysis['bias_detected'] else '✅ 정상'
                html += f"""
                <div style="background: white; padding: 15px; border: 1px solid #ddd; margin: 10px 0; border-radius: 5px;">
                    <h4>{attr} 분석 - {bias_status}</h4>
                    <p>{analysis['interpretation']}</p>
                    <ul style="font-size: 0.9em; color: #666;">
                        <li>형평성 비율: {analysis['statistical_tests']['parity_ratio']}</li>
                        <li>p-value: {analysis['statistical_tests']['p_value']}</li>
                        <li>효과 크기(Cohen's d): {analysis['statistical_tests']['cohen_d']}</li>
                    </ul>
                </div>
                """
        
        # 권고사항
        html += """
            <div style="margin: 20px 0;">
                <h3>💡 권고사항</h3>
                <ul>
        """
        
        for rec in bias_report['recommendations']:
            html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
        </div>
        """
        
        return html
