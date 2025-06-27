# app/core/analyzers/quantitative_analyzer.py
"""
AIRISS 정량 데이터 분석기 - v3.0에서 이식
"""
import logging
import pandas as pd
from typing import Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class QuantitativeAnalyzer:
    """평가등급, 점수 등 정량데이터 분석 전용 클래스"""
    
    def __init__(self):
        self.grade_mappings = self.setup_grade_mappings()
        self.score_weights = self.setup_score_weights()
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
            
            # OK금융그룹 맞춤 등급 (예상)
            'OK★★★': 100, 'OK★★': 90, 'OK★': 80, 
            'OK A': 75, 'OK B+': 70, 'OK B': 65, 'OK C': 55, 'OK D': 40
        }
    
    def setup_score_weights(self) -> Dict[str, float]:
        """정량 데이터 항목별 가중치 설정"""
        return {
            'performance_grade': 0.30,    # 성과평가 등급
            'kpi_score': 0.25,           # KPI 점수
            'competency_grade': 0.20,    # 역량평가 등급  
            'attendance_score': 0.10,    # 근태점수
            'training_score': 0.10,      # 교육이수 점수
            'certificate_score': 0.05    # 자격증/인증 점수
        }
    
    def extract_quantitative_data(self, row: pd.Series) -> Dict[str, Any]:
        """행 데이터에서 정량적 요소 추출"""
        quant_data = {}
        
        # 컬럼명에서 정량 데이터 패턴 찾기
        for col_name, value in row.items():
            col_lower = str(col_name).lower()
            
            # 점수 관련 컬럼 찾기
            if any(keyword in col_lower for keyword in ['점수', 'score', '평점', 'rating']):
                quant_data[f'score_{col_name}'] = self.normalize_score(value)
            
            # 등급 관련 컬럼 찾기  
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
            return 50.0  # 기본값
        
        grade_str = str(grade_value).strip().upper()
        
        # 직접 매핑 확인
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
        # 숫자 점수인 경우 (0-100)
        try:
            score = float(grade_str)
            if 0 <= score <= 100:
                return score
            elif 0 <= score <= 5:  # 1-5 척도
                return (score - 1) * 25  # 1->0, 2->25, 3->50, 4->75, 5->100
            elif 0 <= score <= 10:  # 1-10 척도
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
        """점수 값 정규화 (0-100 범위로)"""
        if pd.isna(score_value) or score_value == '':
            return 50.0
        
        try:
            score = float(str(score_value).replace('%', '').replace('점', ''))
            
            if 0 <= score <= 1:  # 0-1 범위
                return score * 100
            elif 0 <= score <= 5:  # 1-5 범위
                return (score - 1) * 25
            elif 0 <= score <= 10:  # 1-10 범위
                return score * 10
            elif 0 <= score <= 100:  # 0-100 범위
                return score
            else:
                # 범위 초과시 클리핑
                return max(0, min(100, score))
                
        except (ValueError, TypeError):
            logger.warning(f"점수 변환 실패: {score_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_percentage(self, percent_value) -> float:
        """백분율 정규화"""
        if pd.isna(percent_value) or percent_value == '':
            return 50.0
        
        try:
            # % 기호 제거 후 숫자 추출
            percent_str = str(percent_value).replace('%', '').replace('퍼센트', '')
            percent = float(percent_str)
            
            if 0 <= percent <= 1:  # 0-1 범위 (소수)
                return percent * 100
            elif 0 <= percent <= 100:  # 0-100 범위
                return percent
            else:
                return max(0, min(100, percent))
                
        except (ValueError, TypeError):
            logger.warning(f"백분율 변환 실패: {percent_value}, 기본값 50 적용")
            return 50.0
    
    def normalize_count(self, count_value) -> float:
        """횟수/건수를 점수로 변환 (상대적 평가)"""
        if pd.isna(count_value) or count_value == '':
            return 50.0
        
        try:
            count = float(str(count_value).replace('회', '').replace('건', '').replace('번', ''))
            
            # 임시적으로 로그 스케일 적용 (실제로는 조직 평균과 비교해야 함)
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
        
        # 가중평균 계산 (데이터 유형별)
        total_score = 0.0
        total_weight = 0.0
        contributing_factors = {}
        
        for data_key, score in quant_data.items():
            # 데이터 유형별 가중치 적용
            if 'grade_' in data_key:
                weight = 0.4  # 등급 데이터는 높은 가중치
            elif 'score_' in data_key:
                weight = 0.3  # 점수 데이터
            elif 'rate_' in data_key:
                weight = 0.2  # 비율 데이터
            else:
                weight = 0.1  # 기타
            
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
            confidence = min(total_weight * 20, 100)  # 가중치 합에 따른 신뢰도
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