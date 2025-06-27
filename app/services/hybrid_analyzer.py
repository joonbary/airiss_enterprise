# app/services/hybrid_analyzer.py
"""
AIRISS v4.0 하이브리드 분석기
텍스트 + 정량 데이터 통합 분석 + 편향 탐지
"""

import pandas as pd
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.services.text_analyzer import AIRISSTextAnalyzer
from app.services.quantitative_analyzer import QuantitativeAnalyzer

logger = logging.getLogger(__name__)

class AIRISSHybridAnalyzer:
    """텍스트 + 정량 통합 분석기 with 편향 탐지"""
    
    def __init__(self):
        self.text_analyzer = AIRISSTextAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
        # 편향 탐지 시스템 초기화
        self.bias_detector = None
        try:
            from app.services.bias_detection import BiasDetector
            self.bias_detector = BiasDetector()
            logger.info("✅ 편향 탐지 시스템 로드 완료")
        except ImportError:
            logger.warning("⚠️ 편향 탐지 모듈 없음 - 기본 분석만 수행")
        
        # 통합 가중치
        self.hybrid_weights = {
            'text_analysis': 0.6,
            'quantitative_analysis': 0.4
        }
        
        # 분석 결과 저장 (편향 탐지용)
        self.analysis_history = []
        
        logger.info("✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
    
    def comprehensive_analysis(self, uid: str, opinion: str, row_data: pd.Series) -> Dict[str, Any]:
        """종합 분석: 텍스트 + 정량 + 편향 체크"""
        
        # 1. 텍스트 분석
        text_results = {}
        for dimension in self.text_analyzer.framework.keys():
            text_results[dimension] = self.text_analyzer.analyze_text(opinion, dimension)
        
        text_overall = self.text_analyzer.calculate_overall_score(
            {dim: result["score"] for dim, result in text_results.items()}
        )
        
        # 2. 정량 분석
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row_data)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        
        # 3. 하이브리드 점수 계산
        text_weight = self.hybrid_weights['text_analysis']
        quant_weight = self.hybrid_weights['quantitative_analysis']
        
        # 데이터 품질에 따른 가중치 조정
        if quant_results["data_quality"] == "없음":
            text_weight = 0.8
            quant_weight = 0.2
        elif quant_results["data_quality"] == "낮음":
            text_weight = 0.7
            quant_weight = 0.3
        elif quant_results["data_quality"] == "높음":
            text_weight = 0.5
            quant_weight = 0.5
        
        hybrid_score = (
            text_overall["overall_score"] * text_weight + 
            quant_results["quantitative_score"] * quant_weight
        )
        
        # 4. 통합 신뢰도
        hybrid_confidence = (
            text_overall.get("confidence", 70) * text_weight + 
            quant_results["confidence"] * quant_weight
        )
        
        # 5. 하이브리드 등급
        hybrid_grade_info = self._calculate_hybrid_grade(hybrid_score)
        
        # 6. 설명가능성 정보 추가
        explainability_info = self._generate_explainability(
            text_results, quant_results, text_weight, quant_weight, hybrid_score
        )
        
        # 7. 분석 결과 저장 (편향 탐지용)
        if hasattr(row_data, 'to_dict'):
            analysis_record = {
                'uid': uid,
                'hybrid_score': hybrid_score,
                'timestamp': datetime.now()
            }
            # 보호 속성 추가 (있는 경우)
            for attr in ['성별', '연령대', '부서', '직급']:
                if attr in row_data:
                    analysis_record[attr] = row_data[attr]
            self.analysis_history.append(analysis_record)
        
        return {
            "text_analysis": {
                "overall_score": text_overall["overall_score"],
                "grade": text_overall["grade"],
                "dimension_scores": {dim: result["score"] for dim, result in text_results.items()},
                "dimension_details": text_results
            },
            "quantitative_analysis": quant_results,
            "hybrid_analysis": {
                "overall_score": round(hybrid_score, 1),
                "grade": hybrid_grade_info["grade"],
                "grade_description": hybrid_grade_info["grade_description"],
                "percentile": hybrid_grade_info["percentile"],
                "confidence": round(hybrid_confidence, 1),
                "analysis_composition": {
                    "text_weight": round(text_weight * 100, 1),
                    "quantitative_weight": round(quant_weight * 100, 1)
                }
            },
            "explainability": explainability_info,
            "analysis_metadata": {
                "uid": uid,
                "analysis_version": "AIRISS v4.0 - Hybrid Enhanced",
                "data_sources": {
                    "text_available": bool(opinion and opinion.strip()),
                    "quantitative_available": bool(quant_data),
                    "quantitative_data_quality": quant_results["data_quality"]
                },
                "bias_detection_available": self.bias_detector is not None
            }
        }
    
    def _calculate_hybrid_grade(self, score: float) -> Dict[str, str]:
        """하이브리드 점수를 OK등급으로 변환"""
        if score >= 95:
            return {
                "grade": "OK★★★",
                "grade_description": "최우수 등급 (TOP 1%) - v4.0 하이브리드",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "grade_description": "우수 등급 (TOP 5%) - v4.0 하이브리드",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "grade_description": "우수+ 등급 (TOP 10%) - v4.0 하이브리드",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "grade_description": "양호 등급 (TOP 20%) - v4.0 하이브리드",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "grade_description": "양호- 등급 (TOP 30%) - v4.0 하이브리드",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "grade_description": "보통 등급 (TOP 40%) - v4.0 하이브리드",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "grade_description": "개선필요 등급 (TOP 60%) - v4.0 하이브리드",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "grade_description": "집중개선 등급 (하위 40%) - v4.0 하이브리드",
                "percentile": "하위 40%"
            }
    
    def _generate_explainability(self, 
                               text_results: Dict,
                               quant_results: Dict,
                               text_weight: float,
                               quant_weight: float,
                               hybrid_score: float) -> Dict[str, Any]:
        """점수 산출 근거 설명 생성"""
        
        # 주요 긍정/부정 요인 추출
        positive_factors = []
        negative_factors = []
        
        # 텍스트 분석 요인
        for dimension, result in text_results.items():
            if result['score'] >= 80:
                positive_factors.append({
                    'factor': f"{dimension}",
                    'score': result['score'],
                    'impact': result['score'] * self.text_analyzer.framework[dimension]['weight'] * text_weight,
                    'evidence': result['signals']['positive_words'][:3]
                })
            elif result['score'] < 60:
                negative_factors.append({
                    'factor': f"{dimension}",
                    'score': result['score'],
                    'impact': (100 - result['score']) * self.text_analyzer.framework[dimension]['weight'] * text_weight,
                    'evidence': result['signals']['negative_words'][:3]
                })
        
        # 정량 분석 요인
        if quant_results['quantitative_score'] >= 80:
            positive_factors.append({
                'factor': "정량적 성과",
                'score': quant_results['quantitative_score'],
                'impact': quant_results['quantitative_score'] * quant_weight,
                'evidence': ["KPI 달성", "성과 우수"]
            })
        elif quant_results['quantitative_score'] < 60:
            negative_factors.append({
                'factor': "정량적 성과",
                'score': quant_results['quantitative_score'],
                'impact': (100 - quant_results['quantitative_score']) * quant_weight,
                'evidence': ["KPI 미달", "성과 부진"]
            })
        
        # 상위 3개 요인 정렬
        positive_factors.sort(key=lambda x: x['impact'], reverse=True)
        negative_factors.sort(key=lambda x: x['impact'], reverse=True)
        
        return {
            "score_breakdown": {
                "text_contribution": round(text_results.get('업무성과', {}).get('score', 50) * text_weight, 1),
                "quantitative_contribution": round(quant_results['quantitative_score'] * quant_weight, 1),
                "final_score": round(hybrid_score, 1)
            },
            "key_positive_factors": positive_factors[:3],
            "key_negative_factors": negative_factors[:3],
            "improvement_suggestions": self._generate_improvement_suggestions(negative_factors),
            "confidence_explanation": self._explain_confidence(text_results, quant_results)
        }
    
    def _generate_improvement_suggestions(self, negative_factors: List[Dict]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        for factor in negative_factors[:3]:
            if factor['factor'] == "커뮤니케이션":
                suggestions.append("💡 커뮤니케이션 스킬 향상 교육 참여를 권장합니다.")
            elif factor['factor'] == "리더십협업":
                suggestions.append("💡 팀워크 및 협업 역량 강화 프로그램 참여를 고려하세요.")
            elif factor['factor'] == "전문성학습":
                suggestions.append("💡 직무 관련 전문 교육 및 자격증 취득을 추천합니다.")
            elif factor['factor'] == "업무성과":
                suggestions.append("💡 목표 설정 및 시간 관리 기법 학습이 도움될 것입니다.")
            elif factor['factor'] == "정량적 성과":
                suggestions.append("💡 KPI 달성을 위한 구체적인 실행 계획 수립이 필요합니다.")
        
        return suggestions[:3]  # 최대 3개 제안
    
    def _explain_confidence(self, text_results: Dict, quant_results: Dict) -> str:
        """신뢰도 설명"""
        avg_text_confidence = sum(r.get('confidence', 0) for r in text_results.values()) / len(text_results)
        quant_confidence = quant_results.get('confidence', 0)
        
        if avg_text_confidence >= 80 and quant_confidence >= 80:
            return "높은 신뢰도: 충분한 텍스트 정보와 정량 데이터를 기반으로 분석되었습니다."
        elif avg_text_confidence >= 60 or quant_confidence >= 60:
            return "중간 신뢰도: 일부 데이터가 제한적이지만 의미있는 분석이 가능했습니다."
        else:
            return "낮은 신뢰도: 제한된 정보로 인해 추가 데이터 수집을 권장합니다."
    
    def detect_bias_in_batch(self, analysis_results_df: pd.DataFrame) -> Dict[str, Any]:
        """배치 분석 결과의 편향 탐지"""
        if not self.bias_detector:
            return {
                "error": "편향 탐지 시스템이 설치되지 않았습니다.",
                "recommendation": "bias_detection 모듈을 설치하세요."
            }
        
        try:
            bias_report = self.bias_detector.detect_bias(analysis_results_df)
            return bias_report
        except Exception as e:
            logger.error(f"편향 탐지 오류: {e}")
            return {
                "error": f"편향 탐지 중 오류 발생: {str(e)}",
                "recommendation": "데이터 형식을 확인하세요."
            }
    
    def get_fairness_metrics(self) -> Dict[str, Any]:
        """현재까지 분석된 데이터의 공정성 메트릭"""
        if not self.analysis_history:
            return {
                "status": "no_data",
                "message": "아직 분석된 데이터가 없습니다."
            }
        
        df = pd.DataFrame(self.analysis_history)
        
        metrics = {
            "total_analyzed": len(df),
            "average_score": round(df['hybrid_score'].mean(), 1),
            "score_std": round(df['hybrid_score'].std(), 1),
            "score_distribution": {
                "min": round(df['hybrid_score'].min(), 1),
                "25%": round(df['hybrid_score'].quantile(0.25), 1),
                "50%": round(df['hybrid_score'].quantile(0.50), 1),
                "75%": round(df['hybrid_score'].quantile(0.75), 1),
                "max": round(df['hybrid_score'].max(), 1)
            }
        }
        
        # 보호 속성별 평균 점수
        for attr in ['성별', '연령대', '부서', '직급']:
            if attr in df.columns:
                metrics[f'{attr}_averages'] = df.groupby(attr)['hybrid_score'].mean().to_dict()
        
        return metrics
