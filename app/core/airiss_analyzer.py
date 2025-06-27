"""
AIRISS v4.0 하이브리드 분석 엔진
v3.0의 모든 기능을 클래스 기반으로 재구성
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio

from app.core.airiss_framework import AIRISS_FRAMEWORK, get_ok_grade

logger = logging.getLogger(__name__)

class AIRISSTextAnalyzer:
    """텍스트 기반 분석기"""
    
    def __init__(self):
        self.framework = AIRISS_FRAMEWORK
        self.openai_available = False
        self.openai = None
        
        try:
            import openai
            self.openai = openai
            self.openai_available = True
            logger.info("✅ OpenAI 모듈 로드 성공")
        except ImportError:
            logger.warning("⚠️ OpenAI 모듈 없음 - 키워드 분석만 가능")
    
    def analyze_text(self, text: str, dimension: str) -> Dict[str, Any]:
        """텍스트 분석하여 점수 산출"""
        if not text or text.lower() in ['nan', 'null', '', 'none']:
            return {
                "score": 50, 
                "confidence": 0, 
                "signals": {
                    "positive": 0, 
                    "negative": 0, 
                    "positive_words": [], 
                    "negative_words": []
                }
            }
        
        keywords = self.framework[dimension]["keywords"]
        text_lower = text.lower()
        
        # 키워드 매칭
        positive_matches = []
        negative_matches = []
        
        for word in keywords["positive"]:
            if word in text_lower:
                positive_matches.append(word)
        
        for word in keywords["negative"]:
            if word in text_lower:
                negative_matches.append(word)
        
        positive_count = len(positive_matches)
        negative_count = len(negative_matches)
        
        # 점수 계산 (v3.0 알고리즘)
        base_score = 50
        positive_boost = min(positive_count * 8, 45)
        negative_penalty = min(negative_count * 10, 40)
        
        text_length = len(text)
        if text_length > 50:
            length_bonus = min((text_length - 50) / 100 * 5, 10)
        else:
            length_bonus = 0
        
        final_score = base_score + positive_boost - negative_penalty + length_bonus
        final_score = max(10, min(100, final_score))
        
        # 신뢰도 계산
        total_signals = positive_count + negative_count
        base_confidence = min(total_signals * 12, 80)
        length_confidence = min(text_length / 20, 20)
        confidence = min(base_confidence + length_confidence, 100)
        
        return {
            "score": round(final_score, 1),
            "confidence": round(confidence, 1),
            "signals": {
                "positive": positive_count,
                "negative": negative_count,
                "positive_words": positive_matches[:5],
                "negative_words": negative_matches[:5]
            }
        }
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """종합 점수 계산"""
        weighted_sum = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.framework:
                weight = self.framework[dimension]["weight"]
                weighted_sum += score * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 50
        grade_info = get_ok_grade(overall_score)
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade_info["grade"],
            "grade_description": grade_info["description"],
            "percentile": grade_info["percentile"],
            "weighted_scores": dimension_scores
        }

class QuantitativeAnalyzer:
    """평가등급, 점수 등 정량데이터 분석 전용 클래스"""
    
    def __init__(self):
        self.grade_mappings = self.setup_grade_mappings()
        logger.info("✅ 정량데이터 분석기 초기화 완료")
    
    def setup_grade_mappings(self) -> Dict[str, float]:
        """다양한 평가등급 형식을 점수로 변환하는 매핑 테이블"""
        return {
            # 5단계 등급
            'S': 100, 'A': 85, 'B': 70, 'C': 55, 'D': 40,
            
            # 영문 등급  
            'A+': 100, 'A': 95, 'A-': 90,
            'B+': 85, 'B': 80, 'B-': 75,
            'C+': 70, 'C': 65, 'C-': 60,
            'D+': 55, 'D': 50, 'D-': 45,
            'F': 30,
            
            # 숫자 등급
            '1': 100, '2': 80, '3': 60, '4': 40, '5': 20,
            '1급': 100, '2급': 80, '3급': 60, '4급': 40, '5급': 20,
            
            # 한글 등급
            '우수': 90, '양호': 75, '보통': 60, '미흡': 45, '부족': 30,
            '최우수': 100, '상': 85, '중': 65, '하': 45,
            
            # 백분위/퍼센트
            '상위10%': 95, '상위20%': 85, '상위30%': 75, 
            '상위50%': 65, '하위50%': 50, '하위30%': 35,
            
            # OK금융그룹 맞춤 등급
            'OK★★★': 100, 'OK★★': 90, 'OK★': 80, 
            'OK A': 75, 'OK B+': 70, 'OK B': 65, 'OK C': 55, 'OK D': 40
        }
    
    def extract_quantitative_data(self, row: pd.Series) -> Dict[str, Any]:
        """행 데이터에서 정량적 요소 추출"""
        quant_data = {}
        
        for col_name, value in row.items():
            col_lower = str(col_name).lower()
            
            # 점수 관련 컬럼
            if any(keyword in col_lower for keyword in ['점수', 'score', '평점', 'rating']):
                quant_data[f'score_{col_name}'] = self.normalize_score(value)
            
            # 등급 관련 컬럼
            elif any(keyword in col_lower for keyword in ['등급', 'grade', '평가', 'level']):
                quant_data[f'grade_{col_name}'] = self.convert_grade_to_score(value)
            
            # 달성률/백분율 관련
            elif any(keyword in col_lower for keyword in ['달성률', '비율', 'rate', '%', 'percent']):
                quant_data[f'rate_{col_name}'] = self.normalize_percentage(value)
            
            # 횟수/건수 관련
            elif any(keyword in col_lower for keyword in ['횟수', '건수', 'count', '회', '번']):
                quant_data[f'count_{col_name}'] = self.normalize_count(value)
                
        return quant_data
    
    def convert_grade_to_score(self, grade_value) -> float:
        """등급을 점수로 변환"""
        if pd.isna(grade_value) or grade_value == '':
            return 50.0
        
        grade_str = str(grade_value).strip().upper()
        
        # 직접 매핑 확인
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
        # 숫자 점수인 경우
        try:
            score = float(grade_str)
            if 0 <= score <= 100:
                return score
            elif 0 <= score <= 5:
                return (score - 1) * 25
            elif 0 <= score <= 10:
                return score * 10
        except ValueError:
            pass
        
        # 패턴 매칭
        if '우수' in grade_str or 'excellent' in grade_str.lower():
            return 90.0
        elif '양호' in grade_str or 'good' in grade_str.lower():
            return 75.0
        elif '보통' in grade_str or 'average' in grade_str.lower():
            return 60.0
        elif '미흡' in grade_str or 'poor' in grade_str.lower():
            return 45.0
        
        logger.warning(f"알 수 없는 등급 형식: {grade_value}, 기본값 50 적용")
        return 50.0
    
    def normalize_score(self, score_value) -> float:
        """점수 값 정규화"""
        if pd.isna(score_value) or score_value == '':
            return 50.0
        
        try:
            score = float(str(score_value).replace('%', '').replace('점', ''))
            
            if 0 <= score <= 1:
                return score * 100
            elif 0 <= score <= 5:
                return (score - 1) * 25
            elif 0 <= score <= 10:
                return score * 10
            elif 0 <= score <= 100:
                return score
            else:
                return max(0, min(100, score))
                
        except (ValueError, TypeError):
            logger.warning(f"점수 변환 실패: {score_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_percentage(self, percent_value) -> float:
        """백분율 정규화"""
        if pd.isna(percent_value) or percent_value == '':
            return 50.0
        
        try:
            percent_str = str(percent_value).replace('%', '').replace('퍼센트', '')
            percent = float(percent_str)
            
            if 0 <= percent <= 1:
                return percent * 100
            elif 0 <= percent <= 100:
                return percent
            else:
                return max(0, min(100, percent))
                
        except (ValueError, TypeError):
            logger.warning(f"백분율 변환 실패: {percent_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_count(self, count_value) -> float:
        """횟수/건수를 점수로 변환"""
        if pd.isna(count_value) or count_value == '':
            return 50.0
        
        try:
            count = float(str(count_value).replace('회', '').replace('건', '').replace('번', ''))
            
            # 로그 스케일 적용
            if count <= 0:
                return 30.0
            elif count <= 2:
                return 50.0
            elif count <= 5:
                return 70.0
            elif count <= 10:
                return 85.0
            else:
                return 95.0
                
        except (ValueError, TypeError):
            logger.warning(f"횟수 변환 실패: {count_value}, 기본값 50 적용")
            return 50.0
    
    def calculate_quantitative_score(self, quant_data: Dict[str, float]) -> Dict[str, Any]:
        """정량 데이터들을 종합하여 최종 점수 계산"""
        if not quant_data:
            return {
                "quantitative_score": 50.0,
                "confidence": 0.0,
                "contributing_factors": {},
                "data_quality": "없음",
                "data_count": 0
            }
        
        # 가중평균 계산
        total_score = 0.0
        total_weight = 0.0
        contributing_factors = {}
        
        for data_key, score in quant_data.items():
            # 데이터 유형별 가중치
            if 'grade_' in data_key:
                weight = 0.4
            elif 'score_' in data_key:
                weight = 0.3
            elif 'rate_' in data_key:
                weight = 0.2
            else:
                weight = 0.1
            
            total_score += score * weight
            total_weight += weight
            contributing_factors[data_key] = {
                "score": round(score, 1),
                "weight": weight,
                "contribution": round(score * weight, 1)
            }
        
        # 최종 점수 계산
        if total_weight > 0:
            final_score = total_score / total_weight
            confidence = min(total_weight * 20, 100)
        else:
            final_score = 50.0
            confidence = 0.0
        
        # 데이터 품질 평가
        data_count = len(quant_data)
        if data_count >= 5:
            data_quality = "높음"
        elif data_count >= 3:
            data_quality = "중간"
        elif data_count >= 1:
            data_quality = "낮음"
        else:
            data_quality = "없음"
        
        return {
            "quantitative_score": round(final_score, 1),
            "confidence": round(confidence, 1),
            "contributing_factors": contributing_factors,
            "data_quality": data_quality,
            "data_count": data_count
        }

class AIRISSHybridAnalyzer:
    """텍스트 분석 + 정량 분석 통합 클래스"""
    
    def __init__(self):
        self.text_analyzer = AIRISSTextAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
        # 통합 가중치 설정
        self.hybrid_weights = {
            'text_analysis': 0.6,
            'quantitative_analysis': 0.4
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
        hybrid_confidence = (text_overall.get("confidence", 70) * text_weight + 
                           quant_results["confidence"] * quant_weight)
        
        # 5. 하이브리드 등급 산정
        hybrid_grade_info = get_ok_grade(hybrid_score)
        
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
                "grade_description": hybrid_grade_info["description"],
                "percentile": hybrid_grade_info["percentile"],
                "confidence": round(hybrid_confidence, 1),
                "analysis_composition": {
                    "text_weight": round(text_weight * 100, 1),
                    "quantitative_weight": round(quant_weight * 100, 1)
                }
            },
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
    
    def text_only_analysis(self, uid: str, opinion: str) -> Dict[str, Any]:
        """텍스트 분석만 수행"""
        text_results = {}
        for dimension in AIRISS_FRAMEWORK.keys():
            text_results[dimension] = self.text_analyzer.analyze_text(opinion, dimension)
        
        text_overall = self.text_analyzer.calculate_overall_score(
            {dim: result["score"] for dim, result in text_results.items()}
        )
        
        return {
            "text_analysis": text_overall,
            "quantitative_analysis": {"quantitative_score": 50, "confidence": 0},
            "hybrid_analysis": text_overall,
            "analysis_metadata": {"analysis_version": "AIRISS v4.0 - Text Only"}
        }
    
    def quantitative_only_analysis(self, uid: str, row_data: pd.Series) -> Dict[str, Any]:
        """정량 분석만 수행"""
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row_data)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        grade_info = get_ok_grade(quant_results["quantitative_score"])
        
        return {
            "text_analysis": {"overall_score": 50, "grade": "OK C"},
            "quantitative_analysis": quant_results,
            "hybrid_analysis": {
                "overall_score": quant_results["quantitative_score"],
                "grade": grade_info["grade"],
                "grade_description": grade_info["description"],
                "confidence": quant_results["confidence"]
            },
            "analysis_metadata": {"analysis_version": "AIRISS v4.0 - Quantitative Only"}
        }