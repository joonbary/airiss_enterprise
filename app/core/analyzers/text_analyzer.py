# app/core/analyzers/text_analyzer.py
"""
AIRISS 텍스트 분석기 - v3.0에서 이식
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .framework import AIRISS_FRAMEWORK

logger = logging.getLogger(__name__)


class AIRISSAnalyzer:
    """AIRISS 텍스트 분석 엔진"""
    
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
        
        # 키워드 매칭 - 부분 매칭도 포함
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
        
        # 등급 체계
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
    
    async def generate_ai_feedback(self, uid: str, opinion: str, api_key: str = None, 
                                   model: str = "gpt-3.5-turbo", max_tokens: int = 1200) -> Dict[str, Any]:
        """OpenAI를 사용한 상세 AI 피드백 생성"""
        logger.info(f"AI 피드백 생성 시작: {uid}, API 키 존재: {bool(api_key)}, 모델: {model}")
        
        if not self.openai_available:
            logger.warning("OpenAI 모듈이 설치되지 않음")
            return {
                "ai_strengths": "OpenAI 모듈이 설치되지 않았습니다. 'pip install openai'로 설치해주세요.",
                "ai_weaknesses": "OpenAI 모듈이 설치되지 않았습니다.",
                "ai_feedback": "키워드 기반 분석만 제공됩니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "OpenAI 모듈 미설치"
            }
        
        if not api_key or api_key.strip() == "":
            logger.warning("OpenAI API 키가 제공되지 않음")
            return {
                "ai_strengths": "OpenAI API 키가 제공되지 않았습니다.",
                "ai_weaknesses": "API 키를 입력하면 상세한 개선점 분석을 받을 수 있습니다.",
                "ai_feedback": "키워드 기반 분석만 수행되었습니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "API 키 없음"
            }
        
        if not api_key.startswith('sk-'):
            logger.warning("잘못된 API 키 형식")
            return {
                "ai_strengths": "잘못된 API 키 형식입니다.",
                "ai_weaknesses": "올바른 OpenAI API 키를 입력해주세요.",
                "ai_feedback": "API 키는 'sk-'로 시작해야 합니다.",
                "processing_time": 0,
                "model_used": "none",
                "tokens_used": 0,
                "error": "잘못된 API 키 형식"
            }
        
        start_time = datetime.now()
        
        try:
            client = self.openai.OpenAI(api_key=api_key.strip())
            
            prompt = self.create_ok_prompt(uid, opinion, model, max_tokens)
            
            logger.info(f"OpenAI API 호출 시작: 모델={model}, 토큰={max_tokens}")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 OK금융그룹의 전문 HR 분석가입니다. AIRISS 8대 영역을 기반으로 직원 평가를 분석합니다."
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
            logger.info(f"OpenAI API 응답 수신 완료: {len(feedback_text)}자")
            
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
            
            if "api_key" in error_msg.lower():
                error_detail = "API 키가 잘못되었거나 만료되었습니다."
            elif "quota" in error_msg.lower():
                error_detail = "API 사용량 한도를 초과했습니다."
            elif "model" in error_msg.lower():
                error_detail = f"모델 '{model}'에 접근할 수 없습니다."
            elif "timeout" in error_msg.lower():
                error_detail = "API 응답 시간이 초과되었습니다."
            else:
                error_detail = f"API 오류: {error_msg}"
            
            return {
                "ai_strengths": f"AI 분석 오류: {error_detail}",
                "ai_weaknesses": "AI 분석을 완료할 수 없습니다.",
                "ai_feedback": f"OpenAI API 호출 중 오류가 발생했습니다: {error_detail}",
                "processing_time": round(processing_time, 2),
                "model_used": model,
                "tokens_used": 0,
                "error": error_detail
            }
    
    def create_ok_prompt(self, uid: str, opinion: str, model: str, max_tokens: int) -> str:
        """OK금융그룹 맞춤 AI 프롬프트 생성"""
        return f"""
OK금융그룹 직원 {uid}의 평가 의견을 AIRISS 8대 영역을 기반으로 종합 분석해주세요.

【평가 의견】
{opinion[:1500]}

【AIRISS 8대 영역 (OK금융그룹 가중치)】
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
OK금융그룹 인재상과 AIRISS 8대 영역을 종합하여 실행 가능한 피드백을 500-700자로 작성
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
                strengths = "AIRISS 분석을 통해 긍정적 특성이 관찰됩니다."
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