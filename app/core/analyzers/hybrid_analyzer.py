# app/core/analyzers/hybrid_analyzer.py
"""
AIRISS 하이브리드 분석기 - 텍스트 + 정량 통합
"""
import logging
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from .text_analyzer import AIRISSAnalyzer
from .quantitative_analyzer import QuantitativeAnalyzer
from .framework import AIRISS_FRAMEWORK

logger = logging.getLogger(__name__)


class AIRISSHybridAnalyzer:
    """텍스트 분석 + 정량 분석 통합 클래스"""
    
    def __init__(self):
        # 기존 분석기들
        self.text_analyzer = AIRISSAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
        # 통합 가중치 설정
        self.hybrid_weights = {
            'text_analysis': 0.6,      # 텍스트 분석 60%
            'quantitative_analysis': 0.4  # 정량 분석 40%
        }
        
        logger.info("✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
    
    def comprehensive_analysis(self, uid: str, opinion: str, row_data: pd.Series) -> Dict[str, Any]:
        """종합 분석: 텍스트 + 정량 데이터"""
        
        # 1. 텍스트 분석
        text_results = {}
        for dimension in AIRISS_FRAMEWORK.keys():
            text_results[dimension] = self.text_analyzer.analyze_text(opinion, dimension)
        
        text_overall = self.text_analyzer.calculate_overall_score(
            {dim: result["score"] for dim, result in text_results.items()}
        )
        
        # 2. 정량 데이터 분석
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row_data)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        
        # 3. 하이브리드 점수 계산
        text_weight = self.hybrid_weights['text_analysis']
        quant_weight = self.hybrid_weights['quantitative_analysis']
        
        # 정량 데이터가 없으면 텍스트 분석에 더 의존
        if quant_results["data_quality"] == "없음":
            text_weight = 0.8
            quant_weight = 0.2
        elif quant_results["data_quality"] == "낮음":
            text_weight = 0.7
            quant_weight = 0.3
        
        hybrid_score = (text_overall["overall_score"] * text_weight + 
                       quant_results["quantitative_score"] * quant_weight)
        
        # 4. 통합 신뢰도 계산
        text_confidence = 70  # 기본 텍스트 신뢰도
        for result in text_results.values():
            text_confidence = max(text_confidence, result.get("confidence", 0))
        
        hybrid_confidence = (text_confidence * text_weight + 
                           quant_results["confidence"] * quant_weight)
        
        # 5. 하이브리드 등급 산정
        hybrid_grade_info = self.calculate_hybrid_grade(hybrid_score)
        
        return {
            # 텍스트 분석 결과
            "text_analysis": {
                "overall_score": text_overall["overall_score"],
                "grade": text_overall["grade"],
                "dimension_scores": {dim: result["score"] for dim, result in text_results.items()},
                "dimension_details": text_results
            },
            
            # 정량 분석 결과
            "quantitative_analysis": quant_results,
            
            # 하이브리드 통합 결과
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
            
            # 메타 정보
            "analysis_metadata": {
                "uid": uid,
                "analysis_version": "AIRISS v4.0",
                "analysis_timestamp": datetime.now().isoformat(),
                "data_sources": {
                    "text_available": bool(opinion and opinion.strip()),
                    "quantitative_available": bool(quant_data),
                    "quantitative_data_quality": quant_results["data_quality"]
                }
            }
        }
    
    def calculate_hybrid_grade(self, score: float) -> Dict[str, str]:
        """하이브리드 점수를 OK등급으로 변환"""
        if score >= 95:
            return {
                "grade": "OK★★★",
                "grade_description": "최우수 등급 (TOP 1%) - 정량+정성 통합분석",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "grade_description": "우수 등급 (TOP 5%) - 정량+정성 통합분석",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "grade_description": "우수+ 등급 (TOP 10%) - 정량+정성 통합분석",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "grade_description": "양호 등급 (TOP 20%) - 정량+정성 통합분석",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "grade_description": "양호- 등급 (TOP 30%) - 정량+정성 통합분석",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "grade_description": "보통 등급 (TOP 40%) - 정량+정성 통합분석",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "grade_description": "개선필요 등급 (TOP 60%) - 정량+정성 통합분석",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "grade_description": "집중개선 등급 (하위 40%) - 정량+정성 통합분석",
                "percentile": "하위 40%"
            }