# app/services/quantitative_analyzer.py
"""
AIRISS v4.0 정량 데이터 분석기
평가등급, 점수 등 정량적 데이터 처리
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class QuantitativeAnalyzer:
    """정량 데이터 전문 분석기"""
    
    def __init__(self):
        self.grade_mappings = self._setup_grade_mappings()
        logger.info("✅ 정량 데이터 분석기 초기화 완료")
    
    def _setup_grade_mappings(self) -> Dict[str, float]:
        """등급을 점수로 변환하는 매핑 테이블"""
        return {
            # 5단계 등급
            'S': 100, 'A': 85, 'B': 70, 'C': 55, 'D': 40,
            
            # 영문 상세 등급
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
            '최우수': 100, '탁월': 95, '상': 85, '중': 65, '하': 45,
            
            # 백분위
            '상위10%': 95, '상위20%': 85, '상위30%': 75,
            '상위50%': 65, '하위50%': 50, '하위30%': 35, '하위10%': 20
        }
    
    def extract_quantitative_data(self, row: pd.Series) -> Dict[str, Any]:
        """행 데이터에서 정량적 요소 추출"""
        quant_data = {}
        
        for col_name, value in row.items():
            if pd.isna(value) or value == '':
                continue
                
            col_lower = str(col_name).lower()
            
            # 점수 관련
            if any(kw in col_lower for kw in ['점수', 'score', '평점', 'rating']):
                normalized = self._normalize_score(value)
                if normalized is not None:
                    quant_data[f'score_{col_name}'] = normalized
            
            # 등급 관련
            elif any(kw in col_lower for kw in ['등급', 'grade', '평가', 'level']):
                converted = self._convert_grade_to_score(value)
                if converted is not None:
                    quant_data[f'grade_{col_name}'] = converted
            
            # 달성률/비율 관련
            elif any(kw in col_lower for kw in ['달성률', '비율', 'rate', '%', 'percent']):
                normalized = self._normalize_percentage(value)
                if normalized is not None:
                    quant_data[f'rate_{col_name}'] = normalized
            
            # 횟수/건수 관련
            elif any(kw in col_lower for kw in ['횟수', '건수', 'count', '회', '번']):
                normalized = self._normalize_count(value)
                if normalized is not None:
                    quant_data[f'count_{col_name}'] = normalized
        
        return quant_data
    
    def _convert_grade_to_score(self, grade_value) -> Optional[float]:
        """등급을 점수로 변환"""
        try:
            grade_str = str(grade_value).strip().upper()
            
            # 직접 매핑
            if grade_str in self.grade_mappings:
                return float(self.grade_mappings[grade_str])
            
            # 숫자인 경우
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
            
            return None
            
        except:
            return None
    
    def _normalize_score(self, score_value) -> Optional[float]:
        """점수 정규화 (0-100)"""
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
                
        except:
            return None
    
    def _normalize_percentage(self, percent_value) -> Optional[float]:
        """백분율 정규화"""
        try:
            percent_str = str(percent_value).replace('%', '').replace('퍼센트', '')
            percent = float(percent_str)
            
            if 0 <= percent <= 1:
                return percent * 100
            elif 0 <= percent <= 100:
                return percent
            else:
                return max(0, min(100, percent))
                
        except:
            return None
    
    def _normalize_count(self, count_value) -> Optional[float]:
        """횟수를 점수로 변환"""
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
                
        except:
            return None
    
    def calculate_quantitative_score(self, quant_data: Dict[str, float]) -> Dict[str, Any]:
        """정량 데이터 종합 점수 계산"""
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
        
        # 최종 점수
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
    
    def analyze_row(self, row: pd.Series) -> Dict[str, Any]:
        """행 데이터 전체 분석"""
        quant_data = self.extract_quantitative_data(row)
        quant_results = self.calculate_quantitative_score(quant_data)
        
        # 등급 산정
        score = quant_results["quantitative_score"]
        if score >= 90:
            grade = "OK★★★"
            grade_desc = "최우수 (정량)"
            percentile = "상위 10%"
        elif score >= 80:
            grade = "OK★★"
            grade_desc = "우수 (정량)"
            percentile = "상위 20%"
        elif score >= 70:
            grade = "OK★"
            grade_desc = "양호 (정량)"
            percentile = "상위 30%"
        elif score >= 60:
            grade = "OK A"
            grade_desc = "보통 (정량)"
            percentile = "상위 50%"
        else:
            grade = "OK B"
            grade_desc = "개선필요 (정량)"
            percentile = "하위 50%"
        
        return {
            "text_analysis": {
                "overall_score": 50,
                "grade": "OK C",
                "dimension_scores": {}
            },
            "quantitative_analysis": quant_results,
            "hybrid_analysis": {
                "overall_score": score,
                "grade": grade,
                "grade_description": grade_desc,
                "percentile": percentile,
                "confidence": quant_results["confidence"]
            },
            "analysis_metadata": {
                "analysis_version": "AIRISS v4.0 - Quantitative Only"
            }
        }