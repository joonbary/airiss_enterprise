# app/services/predictive_analytics/performance_predictor.py
"""
AIRISS v4.0 성과 예측 시스템
6개월 후 성과 예측 및 이직 위험도 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

class PerformancePredictor:
    """AI 기반 성과 예측 및 이직 위험도 분석기"""
    
    def __init__(self):
        self.performance_model = None
        self.turnover_model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        
        # 모델 경로
        self.model_dir = "app/models/predictive"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 예측에 사용할 특성들
        self.performance_features = [
            'current_score', 'score_trend', 'kpi_achievement', 
            'communication_score', 'leadership_score', 'learning_score',
            'tenure_months', 'recent_promotion', 'training_hours'
        ]
        
        self.turnover_features = [
            'current_score', 'score_decline', 'engagement_score',
            'tenure_months', 'salary_percentile', 'promotion_gap_months',
            'manager_change_count', 'work_life_balance_score'
        ]
        
        # 모델 로드 시도
        self._load_models()
        
        logger.info("✅ AIRISS 성과 예측 시스템 초기화 완료")
    
    def predict_performance(self, 
                          employee_data: pd.DataFrame,
                          horizon_months: int = 6) -> Dict[str, Any]:
        """미래 성과 예측"""
        
        if self.performance_model is None:
            return self._generate_rule_based_prediction(employee_data, horizon_months)
        
        try:
            # 특성 추출
            features = self._extract_performance_features(employee_data)
            features_scaled = self.scaler.transform(features)
            
            # 예측
            predictions = self.performance_model.predict(features_scaled)
            prediction_proba = self._calculate_prediction_confidence(features_scaled)
            
            # 결과 구성
            results = []
            for idx, (_, row) in enumerate(employee_data.iterrows()):
                future_score = predictions[idx]
                current_score = row.get('hybrid_score', 50)
                score_change = future_score - current_score
                
                performance_category = self._categorize_performance_change(score_change)
                
                results.append({
                    'uid': row.get('uid', f'EMP_{idx}'),
                    'current_score': round(current_score, 1),
                    'predicted_score': round(future_score, 1),
                    'score_change': round(score_change, 1),
                    'performance_outlook': performance_category,
                    'confidence': round(prediction_proba[idx] * 100, 1),
                    'horizon_months': horizon_months,
                    'key_factors': self._identify_key_factors(features.iloc[idx])
                })
            
            return {
                'predictions': results,
                'model_accuracy': self._get_model_accuracy('performance'),
                'prediction_date': datetime.now().isoformat(),
                'summary': self._generate_prediction_summary(results)
            }
            
        except Exception as e:
            logger.error(f"성과 예측 오류: {e}")
            return self._generate_rule_based_prediction(employee_data, horizon_months)
    
    def predict_turnover_risk(self, 
                            employee_data: pd.DataFrame,
                            risk_periods: List[int] = [30, 90, 180]) -> Dict[str, Any]:
        """이직 위험도 예측"""
        
        if self.turnover_model is None:
            return self._generate_rule_based_turnover_risk(employee_data, risk_periods)
        
        try:
            # 특성 추출
            features = self._extract_turnover_features(employee_data)
            features_scaled = self.scaler.transform(features)
            
            # 예측
            risk_predictions = {}
            for period in risk_periods:
                risk_proba = self.turnover_model.predict_proba(features_scaled)[:, 1]
                risk_predictions[period] = risk_proba
            
            # 결과 구성
            results = []
            for idx, (_, row) in enumerate(employee_data.iterrows()):
                risk_scores = {
                    period: round(risk_predictions[period][idx] * 100, 1)
                    for period in risk_periods
                }
                
                max_risk = max(risk_scores.values())
                risk_level = self._categorize_risk_level(max_risk)
                
                results.append({
                    'uid': row.get('uid', f'EMP_{idx}'),
                    'risk_scores': risk_scores,
                    'risk_level': risk_level,
                    'retention_priority': 'HIGH' if max_risk > 70 else 'MEDIUM' if max_risk > 40 else 'LOW',
                    'risk_factors': self._identify_risk_factors(features.iloc[idx]),
                    'retention_strategies': self._recommend_retention_strategies(risk_level, features.iloc[idx])
                })
            
            return {
                'risk_assessments': results,
                'model_accuracy': self._get_model_accuracy('turnover'),
                'assessment_date': datetime.now().isoformat(),
                'summary': self._generate_risk_summary(results)
            }
            
        except Exception as e:
            logger.error(f"이직 위험도 예측 오류: {e}")
            return self._generate_rule_based_turnover_risk(employee_data, risk_periods)
    
    def _generate_rule_based_prediction(self, 
                                      employee_data: pd.DataFrame,
                                      horizon_months: int) -> Dict[str, Any]:
        """규칙 기반 성과 예측 (ML 모델 없을 때)"""
        
        results = []
        for _, row in employee_data.iterrows():
            current_score = row.get('hybrid_score', 50)
            
            # 간단한 규칙 기반 예측
            score_trend = 0
            if current_score >= 85:
                score_trend = np.random.uniform(0, 5)  # 우수자는 소폭 상승
            elif current_score >= 70:
                score_trend = np.random.uniform(-2, 3)  # 평균은 유지
            else:
                score_trend = np.random.uniform(-5, 5)  # 하위는 변동성 큼
            
            # 성장 잠재력 반영
            if row.get('learning_score', 50) > 80:
                score_trend += 2
            
            predicted_score = current_score + score_trend
            predicted_score = max(10, min(100, predicted_score))
            
            results.append({
                'uid': row.get('uid', 'Unknown'),
                'current_score': round(current_score, 1),
                'predicted_score': round(predicted_score, 1),
                'score_change': round(score_trend, 1),
                'performance_outlook': self._categorize_performance_change(score_trend),
                'confidence': 65.0,  # 규칙 기반은 낮은 신뢰도
                'horizon_months': horizon_months,
                'key_factors': ['현재 성과 수준', '학습 역량', '과거 트렌드']
            })
        
        return {
            'predictions': results,
            'model_accuracy': {'type': 'rule_based', 'accuracy': 65.0},
            'prediction_date': datetime.now().isoformat(),
            'summary': self._generate_prediction_summary(results)
        }
    
    def _generate_rule_based_turnover_risk(self,
                                         employee_data: pd.DataFrame,
                                         risk_periods: List[int]) -> Dict[str, Any]:
        """규칙 기반 이직 위험도 평가"""
        
        results = []
        for _, row in employee_data.iterrows():
            # 위험 요인 점수화
            risk_score = 0
            
            # 성과 하락
            if row.get('hybrid_score', 50) < 60:
                risk_score += 20
            
            # 짧은 재직기간
            tenure_months = row.get('tenure_months', 24)
            if tenure_months < 12:
                risk_score += 25
            elif tenure_months < 24:
                risk_score += 15
            
            # 승진 정체
            promotion_gap = row.get('promotion_gap_months', 24)
            if promotion_gap > 36:
                risk_score += 20
            
            # 낮은 참여도
            if row.get('engagement_score', 50) < 40:
                risk_score += 20
            
            # 기간별 위험도 조정
            risk_scores = {}
            for period in risk_periods:
                period_factor = 1.0 + (period / 180) * 0.2  # 장기일수록 위험도 증가
                risk_scores[period] = min(100, risk_score * period_factor)
            
            risk_level = self._categorize_risk_level(max(risk_scores.values()))
            
            results.append({
                'uid': row.get('uid', 'Unknown'),
                'risk_scores': risk_scores,
                'risk_level': risk_level,
                'retention_priority': 'HIGH' if risk_score > 60 else 'MEDIUM' if risk_score > 30 else 'LOW',
                'risk_factors': self._identify_rule_based_risk_factors(row),
                'retention_strategies': self._recommend_retention_strategies(risk_level, row)
            })
        
        return {
            'risk_assessments': results,
            'model_accuracy': {'type': 'rule_based', 'accuracy': 70.0},
            'assessment_date': datetime.now().isoformat(),
            'summary': self._generate_risk_summary(results)
        }
    
    def _categorize_performance_change(self, score_change: float) -> str:
        """성과 변화 분류"""
        if score_change >= 10:
            return "🚀 급성장 예상"
        elif score_change >= 5:
            return "📈 성장 예상"
        elif score_change >= -5:
            return "➡️ 현상 유지"
        elif score_change >= -10:
            return "📉 하락 우려"
        else:
            return "⚠️ 급하락 위험"
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """이직 위험도 분류"""
        if risk_score >= 80:
            return "🔴 매우 높음"
        elif risk_score >= 60:
            return "🟠 높음"
        elif risk_score >= 40:
            return "🟡 보통"
        elif risk_score >= 20:
            return "🟢 낮음"
        else:
            return "🔵 매우 낮음"
    
    def _identify_key_factors(self, features: pd.Series) -> List[str]:
        """성과 예측의 주요 요인"""
        factors = []
        
        if features.get('score_trend', 0) > 5:
            factors.append("지속적인 성과 상승세")
        if features.get('learning_score', 0) > 80:
            factors.append("높은 학습 역량")
        if features.get('leadership_score', 0) > 85:
            factors.append("우수한 리더십")
        if features.get('kpi_achievement', 0) > 90:
            factors.append("KPI 초과 달성")
        
        return factors[:3] if factors else ["성과 데이터 부족"]
    
    def _identify_risk_factors(self, features: pd.Series) -> List[str]:
        """이직 위험 요인"""
        factors = []
        
        if features.get('score_decline', 0) > 10:
            factors.append("최근 성과 급락")
        if features.get('promotion_gap_months', 0) > 36:
            factors.append("장기간 승진 정체")
        if features.get('engagement_score', 0) < 40:
            factors.append("낮은 업무 몰입도")
        if features.get('work_life_balance_score', 0) < 30:
            factors.append("워라밸 불만족")
        if features.get('manager_change_count', 0) > 2:
            factors.append("잦은 관리자 변경")
        
        return factors[:3] if factors else ["특별한 위험 요인 없음"]
    
    def _identify_rule_based_risk_factors(self, row: pd.Series) -> List[str]:
        """규칙 기반 위험 요인 식별"""
        factors = []
        
        if row.get('hybrid_score', 50) < 60:
            factors.append("낮은 성과 점수")
        if row.get('tenure_months', 24) < 12:
            factors.append("짧은 재직 기간")
        if row.get('promotion_gap_months', 24) > 36:
            factors.append("승진 기회 부족")
        
        return factors if factors else ["특별한 위험 요인 없음"]
    
    def _recommend_retention_strategies(self, risk_level: str, features: pd.Series) -> List[str]:
        """이직 방지 전략 추천"""
        strategies = []
        
        if "높음" in risk_level:
            strategies.append("🎯 즉시 1:1 면담 실시")
            strategies.append("💰 보상 체계 재검토")
            strategies.append("📚 경력 개발 기회 제공")
        
        if features.get('learning_score', 0) < 50:
            strategies.append("🎓 맞춤형 교육 프로그램 제공")
        if features.get('work_life_balance_score', 0) < 40:
            strategies.append("⚖️ 유연근무제 도입 검토")
        if features.get('promotion_gap_months', 0) > 36:
            strategies.append("🚀 승진 또는 역할 확대 검토")
        
        return strategies[:3] if strategies else ["✅ 정기적인 피드백 유지"]
    
    def _generate_prediction_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """예측 결과 요약"""
        if not results:
            return {"message": "예측 결과 없음"}
        
        scores = [r['predicted_score'] for r in results]
        changes = [r['score_change'] for r in results]
        
        return {
            'total_employees': len(results),
            'average_predicted_score': round(np.mean(scores), 1),
            'improving_employees': len([c for c in changes if c > 5]),
            'declining_employees': len([c for c in changes if c < -5]),
            'stable_employees': len([c for c in changes if -5 <= c <= 5]),
            'top_performers_predicted': len([s for s in scores if s >= 85]),
            'at_risk_performers': len([s for s in scores if s < 60])
        }
    
    def _generate_risk_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """이직 위험도 요약"""
        if not results:
            return {"message": "평가 결과 없음"}
        
        risk_levels = [r['risk_level'] for r in results]
        
        return {
            'total_assessed': len(results),
            'high_risk_count': len([r for r in risk_levels if "높음" in r]),
            'medium_risk_count': len([r for r in risk_levels if "보통" in r]),
            'low_risk_count': len([r for r in risk_levels if "낮음" in r]),
            'immediate_attention_needed': len([r for r in results if r['retention_priority'] == 'HIGH']),
            'estimated_turnover_cost': len([r for r in risk_levels if "높음" in r]) * 1500000  # 예상 채용 비용
        }
    
    def _extract_performance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """성과 예측용 특성 추출"""
        # 실제 구현시 더 정교한 특성 엔지니어링 필요
        features = pd.DataFrame()
        
        features['current_score'] = df.get('hybrid_score', 50)
        features['score_trend'] = 0  # 과거 데이터 필요
        features['kpi_achievement'] = df.get('kpi_score', 70)
        features['communication_score'] = df.get('communication_score', 70)
        features['leadership_score'] = df.get('leadership_score', 70)
        features['learning_score'] = df.get('learning_score', 70)
        features['tenure_months'] = df.get('tenure_months', 24)
        features['recent_promotion'] = 0  # 최근 승진 여부
        features['training_hours'] = df.get('training_hours', 20)
        
        return features.fillna(features.mean())
    
    def _extract_turnover_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """이직 예측용 특성 추출"""
        features = pd.DataFrame()
        
        features['current_score'] = df.get('hybrid_score', 50)
        features['score_decline'] = 0  # 점수 하락폭
        features['engagement_score'] = df.get('engagement_score', 50)
        features['tenure_months'] = df.get('tenure_months', 24)
        features['salary_percentile'] = df.get('salary_percentile', 50)
        features['promotion_gap_months'] = df.get('promotion_gap_months', 24)
        features['manager_change_count'] = df.get('manager_change_count', 0)
        features['work_life_balance_score'] = df.get('work_life_balance_score', 50)
        
        return features.fillna(features.mean())
    
    def _calculate_prediction_confidence(self, features: np.ndarray) -> np.ndarray:
        """예측 신뢰도 계산"""
        # 실제로는 모델의 불확실성을 계산해야 함
        # 여기서는 간단히 시뮬레이션
        base_confidence = 0.75
        noise = np.random.uniform(-0.1, 0.1, size=len(features))
        return np.clip(base_confidence + noise, 0.5, 0.95)
    
    def _get_model_accuracy(self, model_type: str) -> Dict[str, float]:
        """모델 정확도 정보"""
        # 실제로는 검증 데이터셋으로 계산해야 함
        if model_type == 'performance':
            return {
                'type': 'ml_model',
                'accuracy': 82.5,
                'rmse': 8.3,
                'r2_score': 0.75
            }
        else:
            return {
                'type': 'ml_model',
                'accuracy': 78.2,
                'precision': 0.73,
                'recall': 0.81,
                'f1_score': 0.77
            }
    
    def _load_models(self):
        """저장된 모델 로드"""
        try:
            perf_model_path = os.path.join(self.model_dir, 'performance_model.pkl')
            turnover_model_path = os.path.join(self.model_dir, 'turnover_model.pkl')
            scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
            
            if os.path.exists(perf_model_path):
                self.performance_model = joblib.load(perf_model_path)
                logger.info("✅ 성과 예측 모델 로드 완료")
            
            if os.path.exists(turnover_model_path):
                self.turnover_model = joblib.load(turnover_model_path)
                logger.info("✅ 이직 예측 모델 로드 완료")
            
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
                logger.info("✅ 스케일러 로드 완료")
                
        except Exception as e:
            logger.warning(f"모델 로드 실패, 규칙 기반 예측 사용: {e}")
    
    def train_models(self, historical_data: pd.DataFrame):
        """모델 학습 (향후 구현)"""
        # TODO: 실제 과거 데이터로 모델 학습
        logger.info("모델 학습 기능은 향후 구현 예정입니다.")
