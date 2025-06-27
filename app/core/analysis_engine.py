# app/core/analysis_engine.py
# AIRISS v4.0 완전한 분석 엔진 - v3.0 기능 100% 보존 + 강화

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
import json
import logging
import re
import asyncio

logger = logging.getLogger(__name__)

# AIRISS 8대 영역 완전 설계 (v3.0과 동일하게 보존)
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

class QuantitativeAnalyzer:
    """평가등급, 점수 등 정량데이터 분석 전용 클래스 (v3.0 동일)"""
    
    def __init__(self):
        self.grade_mappings = self.setup_grade_mappings()
        self.score_weights = self.setup_score_weights()
        logger.info("✅ 정량데이터 분석기 초기화 완료")
    
    def setup_grade_mappings(self) -> Dict[str, Dict]:
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
            return 50.0
        
        grade_str = str(grade_value).strip().upper()
        
        if grade_str in self.grade_mappings:
            return float(self.grade_mappings[grade_str])
        
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
        """횟수/건수를 점수로 변환 (상대적 평가)"""
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
        """정량 데이터들을 종합하여 최종 점수 계산"""
        if not quant_data:
            return {
                "quantitative_score": 50.0,
                "confidence": 0.0,
                "contributing_factors": {},
                "data_quality": "없음"
            }
        
        total_score = 0.0
        total_weight = 0.0
        contributing_factors = {}
        
        for data_key, score in quant_data.items():
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
        
        if total_weight > 0:
            final_score = total_score / total_weight
            confidence = min(total_weight * 20, 100)
        else:
            final_score = 50.0
            confidence = 0.0
        
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

class AIRISSAnalyzer:
    """AIRISS 텍스트 분석기 (v3.0 동일)"""
    
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
            return {"score": 50, "confidence": 0, "signals": {"positive": 0, "negative": 0, "positive_words": [], "negative_words": []}}
        
        keywords = self.framework[dimension]["keywords"]
        text_lower = text.lower()
        
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
    
    async def generate_ai_feedback(self, uid: str, opinion: str, api_key: str = None, model: str = "gpt-3.5-turbo", max_tokens: int = 1200) -> Dict[str, Any]:
        """OpenAI를 사용한 상세 AI 피드백 생성"""
        logger.info(f"AI 피드백 생성 시작: {uid}, API 키 존재: {bool(api_key)}, 모델: {model}")
        
        if not self.openai_available:
            logger.warning("OpenAI 모듈이 설치되지 않음")
            return {
                "ai_strengths": "OpenAI 모듈이 설치되지 않았습니다.",
                "ai_weaknesses": "OpenAI 모듈이 설치되지 않았습니다.",
                "ai_feedback": "키워드 기반 분석만 제공됩니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "OpenAI 모듈 미설치"
            }
        
        if not api_key or api_key.strip() == "":
            return {
                "ai_strengths": "OpenAI API 키가 제공되지 않았습니다.",
                "ai_weaknesses": "API 키를 입력하면 상세한 개선점 분석을 받을 수 있습니다.",
                "ai_feedback": "키워드 기반 분석만 수행되었습니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "API 키 없음"
            }
        
        start_time = datetime.now()
        
        try:
            client = self.openai.OpenAI(api_key=api_key.strip())
            
            prompt = self.create_airiss_prompt(uid, opinion, model, max_tokens)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 AIRISS 8대 영역 기반 전문 HR 분석가입니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7,
                timeout=30
            )
            
            feedback_text = response.choices[0].message.content.strip()
            strengths, weaknesses, complete_feedback = self.parse_ai_response(feedback_text)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "ai_strengths": strengths,
                "ai_weaknesses": weaknesses,
                "ai_feedback": complete_feedback,
                "processing_time": round(processing_time, 2),
                "model_used": model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else max_tokens,
                "error": None
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            logger.error(f"OpenAI API 오류: {error_msg}")
            
            return {
                "ai_strengths": f"AI 분석 오류: {error_msg}",
                "ai_weaknesses": "AI 분석을 완료할 수 없습니다.",
                "ai_feedback": f"OpenAI API 호출 중 오류가 발생했습니다: {error_msg}",
                "processing_time": round(processing_time, 2),
                "model_used": model,
                "tokens_used": 0,
                "error": error_msg
            }
    
    def create_airiss_prompt(self, uid: str, opinion: str, model: str, max_tokens: int) -> str:
        """AIRISS 맞춤 AI 프롬프트 생성"""
        return f"""
AIRISS 직원 {uid}의 평가 의견을 8대 영역을 기반으로 종합 분석해주세요.

【평가 의견】
{opinion[:1500]}

【AIRISS 8대 영역】
1. 업무성과 (25%) - 업무 산출물의 양과 질
2. KPI달성 (20%) - 핵심성과지표 달성도  
3. 태도마인드 (15%) - 업무에 대한 태도와 마인드셋
4. 커뮤니케이션 (15%) - 의사소통 능력과 스타일
5. 리더십협업 (10%) - 리더십과 협업 능력
6. 전문성학습 (8%) - 전문성과 학습능력
7. 창의혁신 (5%) - 창의성과 혁신 마인드
8. 조직적응 (2%) - 조직문화 적응도와 윤리성

【출력 형식】
[장점]
1. 핵심장점1 (관련 AIRISS 영역 명시)
2. 핵심장점2 (관련 AIRISS 영역 명시)
3. 핵심장점3 (관련 AIRISS 영역 명시)

[개선점]
1. 개선점1 (관련 AIRISS 영역 명시)
2. 개선점2 (관련 AIRISS 영역 명시)
3. 개선점3 (관련 AIRISS 영역 명시)

[종합 피드백]
AIRISS 8대 영역을 종합하여 실행 가능한 피드백을 500-700자로 작성
        """
    
    def parse_ai_response(self, response: str) -> tuple:
        """AI 응답 파싱"""
        try:
            sections = response.split('[')
            
            strengths = ""
            weaknesses = ""
            feedback = ""
            
            for section in sections:
                section = section.strip()
                if section.startswith('장점]'):
                    content = section.replace('장점]', '').strip()
                    if '[' in content:
                        content = content.split('[')[0].strip()
                    strengths = content
                        
                elif section.startswith('개선점]'):
                    content = section.replace('개선점]', '').strip()
                    if '[' in content:
                        content = content.split('[')[0].strip()
                    weaknesses = content
                        
                elif section.startswith('종합 피드백]') or section.startswith('종합피드백]'):
                    content = section.replace('종합 피드백]', '').replace('종합피드백]', '').strip()
                    feedback = content
            
            if not strengths.strip():
                strengths = "AIRISS 분석을 통해 다음과 같은 긍정적 특성이 관찰됩니다."
            if not weaknesses.strip():
                weaknesses = "전반적으로 우수하나, 지속적인 성장을 위한 개선 기회가 있습니다."
            if not feedback.strip():
                feedback = response
            
            strengths = self.clean_text(strengths)
            weaknesses = self.clean_text(weaknesses)
            feedback = self.clean_text(feedback)
                
            return strengths, weaknesses, feedback
            
        except Exception as e:
            logger.error(f"AI 응답 파싱 오류: {e}")
            return "장점 분석 중 오류 발생", "개선점 분석 중 오류 발생", response
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()

class AIRISSHybridAnalyzer:
    """텍스트 분석 + 정량 분석 통합 클래스 (v3.0 강화)"""
    
    def __init__(self):
        self.text_analyzer = AIRISSAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
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
        
        # 정량 데이터 품질에 따른 가중치 조정
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
        hybrid_grade_info = self.calculate_hybrid_grade(hybrid_score)
        
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
                "grade_description": "최우수 등급 (TOP 1%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "OK★★",
                "grade_description": "우수 등급 (TOP 5%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 5%"
            }
        elif score >= 85:
            return {
                "grade": "OK★",
                "grade_description": "우수+ 등급 (TOP 10%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 10%"
            }
        elif score >= 80:
            return {
                "grade": "OK A",
                "grade_description": "양호 등급 (TOP 20%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 20%"
            }
        elif score >= 75:
            return {
                "grade": "OK B+",
                "grade_description": "양호- 등급 (TOP 30%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 30%"
            }
        elif score >= 70:
            return {
                "grade": "OK B",
                "grade_description": "보통 등급 (TOP 40%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 40%"
            }
        elif score >= 60:
            return {
                "grade": "OK C",
                "grade_description": "개선필요 등급 (TOP 60%) - AIRISS v4.0 하이브리드",
                "percentile": "상위 60%"
            }
        else:
            return {
                "grade": "OK D",
                "grade_description": "집중개선 등급 (하위 40%) - AIRISS v4.0 하이브리드",
                "percentile": "하위 40%"
            }

# 전역 분석기 인스턴스
hybrid_analyzer = AIRISSHybridAnalyzer()

# main.py와의 호환성을 위한 AnalysisEngine alias
AnalysisEngine = AIRISSHybridAnalyzer