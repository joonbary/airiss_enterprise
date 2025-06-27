import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio
import re

from sqlalchemy.orm import Session
from app.models.job import Job

logger = logging.getLogger(__name__)

# AIRISS 8대 영역 프레임워크 (v3.0에서 가져옴)
AIRISS_FRAMEWORK = {
    "업무성과": {
        "keywords": {
            "positive": [
                "우수", "탁월", "뛰어남", "성과", "달성", "완료", "성공", "효율", "생산적", 
                "목표달성", "초과달성", "품질", "정확", "신속", "완벽", "전문적", "체계적",
                "성과가", "결과를", "실적이", "완성도", "만족도"
            ],
            "negative": [
                "부족", "미흡", "지연", "실패", "문제", "오류", "늦음", "비효율", 
                "목표미달", "품질저하", "부정확", "미완성", "부실", "개선", "보완"
            ]
        },
        "weight": 0.25,
        "description": "업무 산출물의 양과 질",
        "color": "#FF5722",
        "icon": "📊"
    },
    "KPI달성": {
        "keywords": {
            "positive": [
                "KPI달성", "지표달성", "목표초과", "성과우수", "실적우수", "매출증가", 
                "효율향상", "생산성향상", "수치달성", "성장", "개선", "달성률", "초과"
            ],
            "negative": [
                "KPI미달", "목표미달", "실적부진", "매출감소", "효율저하", 
                "생산성저하", "수치부족", "하락", "퇴보", "미달"
            ]
        },
        "weight": 0.20,
        "description": "핵심성과지표 달성도",
        "color": "#4A4A4A",
        "icon": "🎯"
    },
    "태도마인드": {
        "keywords": {
            "positive": [
                "적극적", "긍정적", "열정", "성실", "책임감", "진취적", "협조적", 
                "성장지향", "학습의지", "도전정신", "주인의식", "헌신", "열심히", "노력"
            ],
            "negative": [
                "소극적", "부정적", "무관심", "불성실", "회피", "냉소적", 
                "비협조적", "안주", "현상유지", "수동적", "태도", "마인드"
            ]
        },
        "weight": 0.15,
        "description": "업무에 대한 태도와 마인드셋",
        "color": "#F89C26",
        "icon": "🧠"
    },
    "커뮤니케이션": {
        "keywords": {
            "positive": [
                "명확", "정확", "신속", "친절", "경청", "소통", "전달", "이해", 
                "설득", "협의", "조율", "공유", "투명", "개방적", "의사소통", "원활"
            ],
            "negative": [
                "불명확", "지연", "무시", "오해", "단절", "침묵", "회피", 
                "독단", "일방적", "폐쇄적", "소통부족", "전달력"
            ]
        },
        "weight": 0.15,
        "description": "의사소통 능력과 스타일",
        "color": "#B3B3B3",
        "icon": "💬"
    },
    "리더십협업": {
        "keywords": {
            "positive": [
                "리더십", "팀워크", "협업", "지원", "멘토링", "동기부여", "조율", 
                "화합", "팀빌딩", "위임", "코칭", "영향력", "협력", "팀플레이"
            ],
            "negative": [
                "독단", "갈등", "비협조", "소외", "분열", "대립", "이기주의", 
                "방해", "무관심", "고립", "개인주의"
            ]
        },
        "weight": 0.10,
        "description": "리더십과 협업 능력",
        "color": "#FF8A50",
        "icon": "👥"
    },
    "전문성학습": {
        "keywords": {
            "positive": [
                "전문", "숙련", "기술", "지식", "학습", "발전", "역량", "능력", 
                "성장", "향상", "습득", "개발", "전문성", "노하우", "스킬", "경험"
            ],
            "negative": [
                "미숙", "부족", "낙후", "무지", "정체", "퇴보", "무능력", 
                "기초부족", "역량부족", "실력부족"
            ]
        },
        "weight": 0.08,
        "description": "전문성과 학습능력",
        "color": "#6A6A6A",
        "icon": "📚"
    },
    "창의혁신": {
        "keywords": {
            "positive": [
                "창의", "혁신", "아이디어", "개선", "효율화", "최적화", "새로운", 
                "도전", "변화", "발상", "창조", "혁신적", "독창적", "창조적"
            ],
            "negative": [
                "보수적", "경직", "틀에박힌", "변화거부", "기존방식", "관습적", 
                "경직된", "고정적", "변화없이"
            ]
        },
        "weight": 0.05,
        "description": "창의성과 혁신 마인드",
        "color": "#FFA726",
        "icon": "💡"
    },
    "조직적응": {
        "keywords": {
            "positive": [
                "적응", "융화", "조화", "문화", "규칙준수", "윤리", "신뢰", 
                "안정", "일관성", "성실성", "조직", "회사", "팀에"
            ],
            "negative": [
                "부적응", "갈등", "위반", "비윤리", "불신", "일탈", 
                "문제행동", "규정위반", "조직과"
            ]
        },
        "weight": 0.02,
        "description": "조직문화 적응도와 윤리성",
        "color": "#9E9E9E",
        "icon": "🏢"
    }
}


class TextAnalyzer:
    """텍스트 분석기"""
    
    def __init__(self):
        self.framework = AIRISS_FRAMEWORK
        logger.info("텍스트 분석기 초기화 완료")
    
    def analyze_text(self, text: str, dimension: str) -> Dict[str, Any]:
        """텍스트를 분석하여 점수 산출"""
        if not text or text.lower() in ['nan', 'null', '', 'none']:
            return {
                "score": 50,
                "confidence": 0,
                "signals": {"positive": 0, "negative": 0, "positive_words": [], "negative_words": []}
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
        
        # 점수 계산
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
        
        # 등급 결정
        if overall_score >= 95:
            grade = "OK★★★"
            grade_desc = "최우수 등급 (TOP 1%)"
            percentile = "상위 1%"
        elif overall_score >= 90:
            grade = "OK★★"
            grade_desc = "우수 등급 (TOP 5%)"
            percentile = "상위 5%"
        elif overall_score >= 85:
            grade = "OK★"
            grade_desc = "우수+ 등급 (TOP 10%)"
            percentile = "상위 10%"
        elif overall_score >= 80:
            grade = "OK A"
            grade_desc = "양호 등급 (TOP 20%)"
            percentile = "상위 20%"
        elif overall_score >= 75:
            grade = "OK B+"
            grade_desc = "양호- 등급 (TOP 30%)"
            percentile = "상위 30%"
        elif overall_score >= 70:
            grade = "OK B"
            grade_desc = "보통 등급 (TOP 40%)"
            percentile = "상위 40%"
        elif overall_score >= 60:
            grade = "OK C"
            grade_desc = "개선필요 등급 (TOP 60%)"
            percentile = "상위 60%"
        else:
            grade = "OK D"
            grade_desc = "집중개선 등급 (하위 40%)"
            percentile = "하위 40%"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "grade_description": grade_desc,
            "percentile": percentile,
            "weighted_scores": dimension_scores
        }


class QuantitativeAnalyzer:
    """정량데이터 분석기"""
    
    def __init__(self):
        self.grade_mappings = self.setup_grade_mappings()
        self.score_weights = self.setup_score_weights()
        logger.info("정량데이터 분석기 초기화 완료")
    
    def setup_grade_mappings(self) -> Dict[str, Dict]:
        """등급 변환 매핑"""
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
    
    def setup_score_weights(self) -> Dict[str, float]:
        """항목별 가중치"""
        return {
            'performance_grade': 0.30,
            'kpi_score': 0.25,
            'competency_grade': 0.20,
            'attendance_score': 0.10,
            'training_score': 0.10,
            'certificate_score': 0.05
        }
    
    def extract_quantitative_data(self, row: pd.Series) -> Dict[str, Any]:
        """정량 데이터 추출"""
        quant_data = {}
        
        for col_name, value in row.items():
            col_lower = str(col_name).lower()
            
            # 점수 관련
            if any(keyword in col_lower for keyword in ['점수', 'score', '평점', 'rating']):
                quant_data[f'score_{col_name}'] = self.normalize_score(value)
            
            # 등급 관련
            elif any(keyword in col_lower for keyword in ['등급', 'grade', '평가', 'level']):
                quant_data[f'grade_{col_name}'] = self.convert_grade_to_score(value)
            
            # 달성률/백분율
            elif any(keyword in col_lower for keyword in ['달성률', '비율', 'rate', '%', 'percent']):
                quant_data[f'rate_{col_name}'] = self.normalize_percentage(value)
            
            # 횟수/건수
            elif any(keyword in col_lower for keyword in ['횟수', '건수', 'count', '회', '번']):
                quant_data[f'count_{col_name}'] = self.normalize_count(value)
                
        return quant_data
    
    def convert_grade_to_score(self, grade_value) -> float:
        """등급을 점수로 변환"""
        if pd.isna(grade_value) or grade_value == '':
            return 50.0
        
        grade_str = str(grade_value).strip().upper()
        
        # 직접 매핑
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
        # 숫자 점수
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
        """점수 정규화"""
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
        """횟수를 점수로 변환"""
        if pd.isna(count_value) or count_value == '':
            return 50.0
        
        try:
            count = float(str(count_value).replace('회', '').replace('건', '').replace('번', ''))
            
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
        """정량 점수 계산"""
        if not quant_data:
            return {
                "quantitative_score": 50.0,
                "confidence": 0.0,
                "contributing_factors": {},
                "data_quality": "없음"
            }
        
        # 가중평균 계산
        total_score = 0.0
        total_weight = 0.0
        contributing_factors = {}
        
        for data_key, score in quant_data.items():
            # 유형별 가중치
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
        
        # 데이터 품질
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


class AIRISSEngine:
    """AIRISS v4.0 하이브리드 분석 엔진"""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        self.hybrid_weights = {
            'text_analysis': 0.6,
            'quantitative_analysis': 0.4
        }
        logger.info("AIRISS v4.0 엔진 초기화 완료")
    
    async def analyze_dataframe(
        self,
        df: pd.DataFrame,
        analysis_mode: str,
        enable_ai: bool,
        api_key: Optional[str],
        model: str,
        max_tokens: int,
        job_id: str,
        db: Session
    ) -> List[Dict[str, Any]]:
        """DataFrame 전체 분석"""
        results = []
        
        # 컬럼 감지
        uid_columns = self._detect_uid_columns(df)
        opinion_columns = self._detect_opinion_columns(df)
        
        for idx, row in df.iterrows():
            try:
                # UID와 의견 추출
                uid = str(row[uid_columns[0]]) if uid_columns else f"user_{idx}"
                opinion = str(row[opinion_columns[0]]) if opinion_columns else ""
                
                # 빈 의견 처리
                if not opinion or opinion.lower() in ['nan', 'null', '', 'none']:
                    if analysis_mode != "quantitative":
                        continue
                    opinion = ""
                
                # 분석 실행
                result = await self.analyze_single_record(
                    uid, opinion, row, analysis_mode, enable_ai, api_key, model, max_tokens
                )
                results.append(result)
                
                # 진행률 업데이트
                progress = (len(results) / len(df)) * 100
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.processed = len(results)
                    job.progress = progress
                    db.commit()
                
                # 속도 조절
                if enable_ai and api_key:
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"개별 분석 오류 - UID {uid}: {e}")
                continue
        
        return results
    
    async def analyze_single_record(
        self,
        uid: str,
        opinion: str,
        row: pd.Series,
        analysis_mode: str,
        enable_ai: bool,
        api_key: Optional[str],
        model: str,
        max_tokens: int
    ) -> Dict[str, Any]:
        """개별 레코드 분석"""
        
        # 텍스트 분석
        text_results = {}
        dimension_scores = {}
        for dimension in AIRISS_FRAMEWORK.keys():
            result = self.text_analyzer.analyze_text(opinion, dimension)
            text_results[dimension] = result
            dimension_scores[dimension] = result["score"]
        
        text_overall = self.text_analyzer.calculate_overall_score(dimension_scores)
        
        # 정량 분석
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        
        # 하이브리드 점수 계산
        if analysis_mode == "text":
            hybrid_score = text_overall["overall_score"]
            hybrid_confidence = text_overall.get("confidence", 70)
        elif analysis_mode == "quantitative":
            hybrid_score = quant_results["quantitative_score"]
            hybrid_confidence = quant_results["confidence"]
        else:  # hybrid
            text_weight = self.hybrid_weights['text_analysis']
            quant_weight = self.hybrid_weights['quantitative_analysis']
            
            # 데이터 품질에 따라 가중치 조정
            if quant_results["data_quality"] == "없음":
                text_weight = 0.8
                quant_weight = 0.2
            elif quant_results["data_quality"] == "낮음":
                text_weight = 0.7
                quant_weight = 0.3
            
            hybrid_score = (text_overall["overall_score"] * text_weight + 
                           quant_results["quantitative_score"] * quant_weight)
            hybrid_confidence = (text_overall.get("confidence", 70) * text_weight + 
                               quant_results["confidence"] * quant_weight)
        
        # 하이브리드 등급 계산
        hybrid_grade_info = self._calculate_hybrid_grade(hybrid_score)
        
        # 결과 생성
        result = {
            "uid": uid,
            "overall_score": round(hybrid_score, 1),
            "grade": hybrid_grade_info["grade"],
            "grade_description": hybrid_grade_info["grade_description"],
            "percentile": hybrid_grade_info["percentile"],
            "text_score": text_overall["overall_score"],
            "quantitative_score": quant_results["quantitative_score"],
            "confidence": round(hybrid_confidence, 1),
            "analysis_mode": analysis_mode,
            "timestamp": datetime.now().isoformat()
        }
        
        # 8대 영역별 점수 추가
        for dimension, score in dimension_scores.items():
            result[f"{dimension}_score"] = score
        
        # AI 피드백 (필요시 추가)
        if enable_ai and api_key:
            # 여기에 OpenAI API 호출 로직 추가
            result["ai_feedback"] = "AI 피드백 기능은 추후 구현 예정입니다."
        
        return result
    
    def _detect_uid_columns(self, df: pd.DataFrame) -> List[str]:
        """UID 컬럼 감지"""
        uid_keywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp']
        uid_columns = []
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in uid_keywords):
                uid_columns.append(col)
        
        return uid_columns
    
    def _detect_opinion_columns(self, df: pd.DataFrame) -> List[str]:
        """의견 컬럼 감지"""
        opinion_keywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review']
        opinion_columns = []
        
        for col in df.columns:
            if any(keyword in col.lower() for keyword in opinion_keywords):
                opinion_columns.append(col)
        
        return opinion_columns
    
    def _calculate_hybrid_grade(self, score: float) -> Dict[str, str]:
        """하이브리드 점수를 OK등급으로 변환"""
        if score >= 95:
            return {
                "grade": "OK★★★",
                "grade_description": "최우수 등급 (TOP 1%)",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "grade_description": "우수 등급 (TOP 5%)",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "grade_description": "우수+ 등급 (TOP 10%)",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "grade_description": "양호 등급 (TOP 20%)",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "grade_description": "양호- 등급 (TOP 30%)",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "grade_description": "보통 등급 (TOP 40%)",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "grade_description": "개선필요 등급 (TOP 60%)",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "grade_description": "집중개선 등급 (하위 40%)",
                "percentile": "하위 40%"
            }